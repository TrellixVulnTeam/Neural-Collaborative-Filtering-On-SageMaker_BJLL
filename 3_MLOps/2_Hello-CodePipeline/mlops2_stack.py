import os
import sys
from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    aws_codecommit as codecommit,
    aws_codepipeline as codepipeline,
    aws_codebuild as codebuild,
    aws_codepipeline_actions as codepipeline_actions,
    aws_lambda as _lambda,
    aws_lambda_event_sources as event_source,
    aws_events_targets as targets,
    aws_events as events,
    aws_sagemaker as sagemaker
)
from constructs import Construct
from aws_cdk import Size
from aws_cdk import Duration

class Mlops2Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        ## Create IAM roles
        sagemaker_role = self.create_iam_role_for_sagemaker()
        codebuild_role = self.create_iam_role_for_codebuild()
        codepipeline_role = self.create_iam_role_for_codepipeline()
        
        
        ## setting parameters
        #repository_name = "mlops-nb"
        
        
        ## Create CodeCommit repository
        #repo = codecommit.Repository(self, "Repository",
        #                             repository_name = repository_name,
        #                             description = "MLOPs repository")
        
        ## Pre-requirement : Create S3 Bucket (ex : mlops-demo-cdk) manually
        #bucket = s3.Bucket(self, "mlops-demo-cdk")
        #bucket_name = bucket.bucket_name
        #bucket_name = "mlops-demo-cdk"


        ## Create SageMaker Notebook with SageMaker_role
        


####################################################################################################################################################################
    
    def create_iam_role_for_sagemaker(self):
        SageMakerRole = iam.Role(
            self,
            "SageMakerRole",
            assumed_by = iam.ServicePrincipal("sagemaker.amazonaws.com"),
            description = "Role for SageMaker Notebook",
            managed_policies = [
                iam.ManagedPolicy.from_aws_managed_policy_name("IAMFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSCodeBuildAdminAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSCodeCommitFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSCodePipelineFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"),
            ],  
        )
        return SageMakerRole
        
        
    def create_iam_role_for_codebuild(self):
        CodeBuildRole = iam.Role(
            self,
            "CodeBuildRole",
            assumed_by = iam.ServicePrincipal("codebuild.amazonaws.com"),
            description = "Role for CodeBuild",
            managed_policies = [
                iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSCodeBuildAdminAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSCodeCommitFullAccess"),
            ],  
        )
        return CodeBuildRole
       
        
    def create_iam_role_for_codepipeline(self):
        CodePipelineRole = iam.Role(
            self,
            "CodePipelineRole",
            assumed_by = iam.CompositePrincipal(
                iam.ServicePrincipal("codebuild.amazonaws.com"),
                iam.ServicePrincipal("codepipeline.amazonaws.com"),
            ),
            description = "Role for CodePipeline",
            managed_policies = [
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSCodeBuildAdminAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSCodePipelineFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSCodeCommitFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSCodeDeployFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
            ],  
        )
        return CodePipelineRole


    def create_lambda_for_uploading_buildspec(self):
        lambda_role = iam.Role(
            self,
            "LambdaRoleInCodecommitHandler",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonRekognitionFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSCodeCommitFullAccess"),
            ],
        )
        handler = _lambda.Function(
            self,
            "Codecommit-handler",
            role=lambda_role,
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="CodecommitHandler.handler",
            # S3에 있는 buildsepc.yml 파일을 codecommit repository에 git add 하는 코드 필요
        )
        