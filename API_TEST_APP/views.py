from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import yt_dlp
import boto3
import os
from uuid import uuid4

# Cloudflare R2 client
s3_client = boto3.client(
    's3',
    endpoint_url=settings.R2_ENDPOINT,
    aws_access_key_id=settings.R2_KEY,
    aws_secret_access_key=settings.R2_SECRET
)

# Path to your YouTube cookies file
COOKIES_FILE_PATH = os.path.join(settings.BASE_DIR, "cookies.txt")  # place cookies.txt in your Django project root

@csrf_exempt
def download_video(request):
    if request.method == "GET":
        return render(request, "download.html")

    elif request.method == "POST":
        url = request.POST.get("url")

        if not url:
            return render(request, "download.html", {"error": "URL is required"})

        temp_filename = str(uuid4())
        output_template = f"{temp_filename}.%(ext)s"

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }

        # Use cookies if available
        if os.path.exists(COOKIES_FILE_PATH):
            ydl_opts["cookiefile"] = COOKIES_FILE_PATH

        try:
            # Download song
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title", "song").replace("/", "_")
                local_file = f"{temp_filename}.mp3"
                cloud_filename = f"{title}.mp3"

            # Upload to Cloudflare R2
            s3_client.upload_file(local_file, settings.R2_BUCKET, cloud_filename)

            # Remove local file
            os.remove(local_file)

            # Clean up old files (keep only 10)
            all_objects = s3_client.list_objects_v2(Bucket=settings.R2_BUCKET).get("Contents", [])
            if len(all_objects) > 10:
                sorted_objects = sorted(all_objects, key=lambda x: x["LastModified"])
                for old_obj in sorted_objects[:-10]:
                    s3_client.delete_object(Bucket=settings.R2_BUCKET, Key=old_obj["Key"])

            # Build file URL
            file_url = f"{settings.R2_PUBLIC_URL}/{cloud_filename}"

            return render(request, "download.html", {
                "success": True,
                "file_url": file_url,
                "file_name": title
            })

        except yt_dlp.utils.DownloadError as e:
            # Specific handling for YouTube login/cookies errors
            if "Sign in to confirm you’re not a bot" in str(e):
                msg = "⚠️ This video requires YouTube login/cookies. Please update cookies.txt."
            else:
                msg = str(e)
            return render(request, "download.html", {"error": msg})

        except Exception as e:
            return render(request, "download.html", {"error": str(e)})

    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
