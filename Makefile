AWS_PROFILE=yandex
BUCKET=waste
PACK:=$(if ${PACK},${PACK},pack1)
BUILD_VERSION:=$(if ${BUILD_VERSION},${BUILD_VERSION},latest)
OAUTH_TOKEN:=$(if ${OAUTH_TOKEN},${OAUTH_TOKEN},oauth-token)

sync:
	aws s3 sync .data/${PACK} s3://${BUCKET}/${PACK} --exclude "*/.DS_Store" --profile ${AWS_PROFILE}

site-sync:
	aws s3 sync frontend-app/my-app/build/static s3://waste-detection/static --profile ${AWS_PROFILE}

ssh-infrastructure:
	ssh -i .ssh/yandex -l angstorm 158.160.17.1

build:
	docker build --platform="linux/amd64" -t angstorm/waste-detection:${BUILD_VERSION} .

yandex-cr-login:
	echo ${OAUTH_TOKEN} | docker login --username oauth --password-stdin cr.yandex

yandex-cr-tag:
	docker tag angstorm/waste-detection:${BUILD_VERSION} cr.yandex/crpv7m9jip4e6uut6oc5/waste-detection:${BUILD_VERSION}

yandex-cr-push:
	docker push cr.yandex/crpv7m9jip4e6uut6oc5/waste-detection:${BUILD_VERSION}

push:
	docker push angstorm/waste-detection:${BUILD_VERSION}