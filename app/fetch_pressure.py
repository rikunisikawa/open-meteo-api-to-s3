import json
import os
from datetime import datetime, timezone

import boto3
import requests

S3_CLIENT = boto3.client("s3")
API_URL = "https://api.open-meteo.com/v1/forecast"


def handler(event, context):
    """
    Open-Meteo APIから気圧データを取得し、S3に保存するLambda関数
    """
    bucket_name = os.environ["BUCKET_NAME"]
    latitude = os.environ["LATITUDE"]
    longitude = os.environ["LONGITUDE"]
    location_name = os.environ["LOCATION_NAME"]

    # Open-Meteo APIから気圧データを取得
    try:
        response = requests.get(
            API_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "hourly": "pressure_msl",
                "timezone": "UTC",
            },
        )
        response.raise_for_status()  # エラーレスポンスの場合は例外を発生させる
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"APIリクエストエラー: {e}")
        return {"statusCode": 500, "body": json.dumps({"message": "APIリクエストエラー"})}

    # 現在の時刻に最も近いデータを抽出
    now_utc = datetime.now(timezone.utc)
    hourly_data = data["hourly"]
    time_list = hourly_data["time"]
    pressure_list = hourly_data["pressure_msl"]

    # 最も近い時刻のインデックスを見つける
    closest_index = min(
        range(len(time_list)),
        key=lambda i: abs(
            datetime.fromisoformat(time_list[i]).replace(tzinfo=timezone.utc) - now_utc
        ),
    )

    recorded_at = time_list[closest_index]
    pressure = pressure_list[closest_index]

    # JSON形式に変換
    output = {
        "recorded_at": recorded_at,
        "pressure": pressure,
        "location": location_name,
    }

    # S3に保存
    try:
        # S3キーを作成
        recorded_at_datetime = datetime.fromisoformat(recorded_at).replace(
            tzinfo=timezone.utc
        )
        year = recorded_at_datetime.strftime("%Y")
        month = recorded_at_datetime.strftime("%m")
        day = recorded_at_datetime.strftime("%d")
        hour = recorded_at_datetime.strftime("%H")
        s3_key = f"pressure/{year}/{month}/{day}/{hour}.json"

        S3_CLIENT.put_object(
            Bucket=bucket_name, Key=s3_key, Body=json.dumps(output).encode("utf-8")
        )
        print(f"S3に保存しました: s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"S3保存エラー: {e}")
        return {"statusCode": 500, "body": json.dumps({"message": "S3保存エラー"})}

    return {"statusCode": 200, "body": json.dumps(output)}
