from __future__ import annotations

from io import StringIO

import pandas as pd


def predict_mock(yolo_model, s3, bucket_name, import_id, task_id):
    """Шаблон функции распознания."""
    bucket = s3.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=import_id).limit(10):
        value = s3.Object(bucket_name, obj.key).get()["Body"].read()
        filename = obj.key.split("/")[-1]
        s3.Object(bucket_name, f"{task_id}/{filename}").put(Body=value)

    d = {"col1": [1, 2], "col2": [3, 4]}
    df = pd.DataFrame(data=d)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer)
    s3.Object(bucket_name, f"{task_id}/result.csv").put(
        Body=csv_buffer.getvalue()
    )
