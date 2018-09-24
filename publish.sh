#!/bin/sh
ROOTDIR=$(dirname $(realpath -s $0))
DISTFILE=${ROOTDIR}/dist/$(basename "${ROOTDIR}")_$(date +%Y%m%d_%H%M%S).zip

cd ${ROOTDIR}
zip "${DISTFILE}" ./*.py >/dev/null 
cd "${VIRTUAL_ENV}"/lib/python2.7/site-packages
zip -ur "${DISTFILE}" ./pytz >/dev/null 
RET=$?
ls -al "${DISTFILE}"

if [ "${RET}" -ne 0 ]; then
	exit ${RET}
fi

aws lambda update-function-code --function-name notify-cloudtrail-events --zip-file fileb://${DISTFILE}
aws lambda update-function-configuration --function-name notify-cloudtrail-events \
  --environment 'Variables={tz=Asia/Tokyo,locale=ja_JP.utf-8,ignore_event_names=,sns_arn=arn:aws:sns:ap-northeast-1:626676598765:notify-aws-service,sns_subject="[AWS]CloudTrail report",target_duration=1hour}' \
  --timeout 15 \
  --memory-size 256
