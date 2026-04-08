import * as cdk from "aws-cdk-lib";
import { aws_opensearchservice as opensearch } from "aws-cdk-lib";
import { execSync } from "node:child_process";
import { Construct } from "constructs";

export class ManagedVectorIngestionStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const accountId = cdk.Stack.of(this).account;
    const region = cdk.Stack.of(this).region;

    const domainName = this.node.tryGetContext("domainName") ?? "handson-vector-xlarge";
    const instanceType = this.node.tryGetContext("instanceType") ?? "or2.xlarge.search";
    const instanceCount = Number(this.node.tryGetContext("instanceCount") ?? "1");
    const ebsVolumeSize = Number(this.node.tryGetContext("ebsVolumeSize") ?? "512");
    const enableS3Vectors = String(this.node.tryGetContext("enableS3Vectors") ?? "false") === "true";
    const enableGpuAcceleration =
      String(this.node.tryGetContext("enableGpuAcceleration") ?? "true") === "true";
    const allowedCidrs = this.resolveAllowedCidrs();

    const domainArn = `arn:aws:es:${region}:${accountId}:domain/${domainName}/*`;
    const accessPolicies = {
      Version: "2012-10-17",
      Statement: [
        {
          Sid: "AllowRootFullAccess",
          Effect: "Allow",
          Principal: { AWS: `arn:aws:iam::${accountId}:root` },
          Action: "es:*",
          Resource: domainArn,
        },
        {
          Sid: "AllowPublicDashboardsAndApiFromAllowedCidrs",
          Effect: "Allow",
          Principal: "*",
          Action: "es:ESHttp*",
          Resource: domainArn,
          Condition: {
            IpAddress: {
              "aws:SourceIp": allowedCidrs,
            },
          },
        },
        {
          Sid: "AllowFutureVectorIngestionRoles",
          Effect: "Allow",
          Principal: "*",
          Action: "es:ESHttp*",
          Resource: domainArn,
          Condition: {
            StringLike: {
              "aws:PrincipalArn": `arn:aws:iam::${accountId}:role/service-role/VectorIngestionRole-*`,
            },
          },
        },
      ],
    };

    const domain = new opensearch.CfnDomain(this, "HandsOnVectorDomain", {
      domainName,
      engineVersion: "OpenSearch_3.1",
      clusterConfig: {
        instanceType,
        instanceCount,
        zoneAwarenessEnabled: false,
      },
      ebsOptions: {
        ebsEnabled: true,
        volumeType: "gp3",
        volumeSize: ebsVolumeSize,
      },
      nodeToNodeEncryptionOptions: {
        enabled: true,
      },
      encryptionAtRestOptions: {
        enabled: true,
      },
      domainEndpointOptions: {
        enforceHttps: true,
        tlsSecurityPolicy: "Policy-Min-TLS-1-2-2019-07",
      },
      accessPolicies,
      advancedOptions: {
        "rest.action.multi.allow_explicit_index": "true",
      },
      aimlOptions: {
        s3VectorsEngine: {
          enabled: enableS3Vectors,
        },
        serverlessVectorAcceleration: {
          enabled: enableGpuAcceleration,
        },
      },
    });

    new cdk.CfnOutput(this, "DomainName", {
      value: domainName,
    });

    new cdk.CfnOutput(this, "DomainEndpoint", {
      value: `https://${domain.attrDomainEndpoint}`,
    });

    new cdk.CfnOutput(this, "DashboardsUrl", {
      value: `https://${domain.attrDomainEndpoint}/_dashboards/`,
    });

    new cdk.CfnOutput(this, "AllowedCidrs", {
      value: allowedCidrs.join(", "),
      description: "OpenSearch Dashboards and public API are open to these CIDRs.",
    });

    new cdk.CfnOutput(this, "S3VectorsEnabled", {
      value: enableS3Vectors ? "true" : "false",
    });

    new cdk.CfnOutput(this, "GpuAccelerationEnabled", {
      value: enableGpuAcceleration ? "true" : "false",
    });
  }

  private resolveAllowedCidrs(): string[] {
    const configuredCidrs = String(this.node.tryGetContext("allowedCidrs") ?? "")
      .split(",")
      .map((value) => value.trim())
      .filter((value) => value.length > 0);

    if (configuredCidrs.length > 0) {
      return configuredCidrs;
    }

    const publicIp = execSync("curl -fsSL https://checkip.amazonaws.com", {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"],
    }).trim();

    if (publicIp.length === 0) {
      throw new Error("グローバル IP を自動検出できませんでした。-c allowedCidrs=203.0.113.10/32 のように指定してください。");
    }

    return [`${publicIp}/32`];
  }
}
