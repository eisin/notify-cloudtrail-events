#!/bin/sh

export tz=Asia/Tokyo
export locale=ja_JP.utf-8
export ignore_event_names=ConsoleLogin:PutEvaluations:CreateLogStream
export sns_arn=arn:aws:sns:ap-northeast-1:626676598765:notify-aws-service
export sns_subject="[AWS]CloudTrail report"
export target_duration=1hour

lambda invoke -v
RET=$?

exit "${RET}"
