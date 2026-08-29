#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";
import { ManagedVectorIngestionStack } from "../lib/managed-vector-ingestion-stack";

const app = new cdk.App();

const account = process.env.CDK_DEFAULT_ACCOUNT ?? process.env.AWS_ACCOUNT_ID;
const region = process.env.CDK_DEFAULT_REGION ?? process.env.AWS_REGION ?? "ap-northeast-1";

if (!account) {
  throw new Error(
    "AWSアカウントを取得できませんでした。AWSプロファイルを設定してから実行してください。",
  );
}

new ManagedVectorIngestionStack(app, "ManagedVectorIngestionStack", {
  env: {
    account,
    region,
  },
});
