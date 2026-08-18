from io import StringIO
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import pipeline


@pytest.mark.parametrize(
    "age, expected",
    [(0, 'young'), (29, 'young'), (30, 'adult'), (31, 'adult')],
)
def test_age_group_boundaries(age, expected):
    assert pipeline.age_group(age) == expected


def test_transform_adds_age_group_column():
    df = pd.DataFrame({'id': [1, 2], 'age': [25, 40]})

    result = pipeline.transform(df)

    assert list(result['age_group']) == ['young', 'adult']


def test_transform_strips_whitespace_from_column_names():
    df = pd.DataFrame({' id ': [1], 'age ': [25]})

    result = pipeline.transform(df)

    assert list(result.columns) == ['id', 'age', 'age_group']


def test_transform_does_not_mutate_input():
    df = pd.DataFrame({'age': [25]})

    pipeline.transform(df)

    assert list(df.columns) == ['age']


def test_upload_sends_dataframe_as_csv_without_index():
    df = pd.DataFrame({'id': [1], 'age': [25], 'age_group': ['young']})
    client = MagicMock()

    with patch.object(pipeline.boto3, 'client', return_value=client) as boto_client:
        pipeline.upload(df, bucket_name='bucket', key='some/key.csv')

    boto_client.assert_called_once_with('s3')
    kwargs = client.put_object.call_args.kwargs
    assert kwargs['Bucket'] == 'bucket'
    assert kwargs['Key'] == 'some/key.csv'
    assert kwargs['Body'] == 'id,age,age_group\n1,25,young\n'


def test_upload_uses_default_bucket_and_key():
    client = MagicMock()

    with patch.object(pipeline.boto3, 'client', return_value=client):
        pipeline.upload(pd.DataFrame({'age': [25]}))

    kwargs = client.put_object.call_args.kwargs
    assert kwargs['Bucket'] == pipeline.BUCKET_NAME
    assert kwargs['Key'] == pipeline.OUTPUT_KEY


def test_process_data_transforms_and_uploads_default_data(capsys):
    client = MagicMock()

    with patch.object(pipeline.boto3, 'client', return_value=client):
        df = pipeline.process_data()

    assert len(df) == 5
    assert list(df['age_group']) == ['adult', 'young', 'adult', 'young', 'adult']

    body = client.put_object.call_args.kwargs['Body']
    uploaded = pd.read_csv(StringIO(body))
    pd.testing.assert_frame_equal(uploaded, df)

    assert 'Uploaded 5 rows' in capsys.readouterr().out


def test_process_data_accepts_custom_csv_and_destination():
    client = MagicMock()
    raw_csv = "id,name,age,city\n9,Zed,20,Denver"

    with patch.object(pipeline.boto3, 'client', return_value=client):
        df = pipeline.process_data(raw_csv=raw_csv, bucket_name='other', key='k.csv')

    assert list(df['age_group']) == ['young']
    kwargs = client.put_object.call_args.kwargs
    assert (kwargs['Bucket'], kwargs['Key']) == ('other', 'k.csv')


def test_process_data_propagates_upload_failure():
    client = MagicMock()
    client.put_object.side_effect = RuntimeError('s3 down')

    with patch.object(pipeline.boto3, 'client', return_value=client):
        with pytest.raises(RuntimeError, match='s3 down'):
            pipeline.process_data()
