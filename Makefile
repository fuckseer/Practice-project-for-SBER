AWS_PROFILE=yandex
BUCKET=waste
PACK=pack1

sync:
	aws s3 sync .data/${PACK} s3://${BUCKET}/${PACK} --exclude "*/.DS_Store" --profile ${AWS_PROFILE}

ssh-infrastructure:
	ssh -i .ssh/yandex -l angstorm 158.160.17.1