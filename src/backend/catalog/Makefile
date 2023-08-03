reserve-flight-payment:
	sam local invoke \
		--event src/reserve-flight/event.json \
		--env-vars local-env-vars.json ReserveFlightSeat \
		--profile ${PROFILE}

release-flight-payment:
	sam local invoke \
		--event src/release-flight/event.json \
		--env-vars local-env-vars.json ReleaseFlightSeat \
		--profile ${PROFILE}

deploy: ##=> Deploy payment service using SAM
# [24-07-2020] Changed from `sam deploy` to `aws cloudformation deploy`
# known issue: https://github.com/awslabs/aws-sam-cli/issues/1698
	$(info [*] Packaging and deploying Payment service...)
	sam package \
		--s3-bucket $${DEPLOYMENT_BUCKET_NAME} \
		--output-template-file packaged.yaml && \
	aws cloudformation deploy \
		--template-file packaged.yaml \
		--stack-name $${STACK_NAME}-catalog-$${AWS_BRANCH} \
		--capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
		--parameter-overrides \
			Stage=$${AWS_BRANCH} \
			FlightTable=/$${AWS_BRANCH}/service/amplify/storage/table/flight

delete: ##=> Delete payment service
	aws cloudformation delete-stack --stack-name $${STACK_NAME}-catalog-$${AWS_BRANCH}