AWS_PROFILE=yandex
BUCKET=waste
PACK=pack1

sync:
	aws s3 sync .data/${PACK} s3://${BUCKET}/${PACK} --exclude "*/.DS_Store" --profile ${AWS_PROFILE}