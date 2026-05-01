import pytest
import pandas as pd
import os
import joblib
from unittest.mock import patch, MagicMock, AsyncMock
from ml_pipeline.data_generator import generate_disaster_data
from ml_pipeline.train import load_data, train_severity_model, train_resource_model, train_risk_prediction_model

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'temp': [25.0, 35.0, 45.0, 20.0, 30.0],
        'rainfall': [0.0, 100.0, 200.0, 50.0, 150.0],
        'wind_speed': [10.0, 50.0, 100.0, 20.0, 80.0],
        'pop_density': [500.0, 2000.0, 5000.0, 1000.0, 3000.0],
        'historical_freq': [1.0, 5.0, 8.0, 2.0, 4.0],
        'water_level': [0.1, 2.0, 5.0, 1.0, 3.0],
        'seismic_mag': [0.0, 0.0, 0.0, 0.0, 0.0],
        'smoke_ppm': [10.0, 100.0, 500.0, 50.0, 250.0],
        'humidity': [50.0, 40.0, 30.0, 60.0, 45.0],
        'severity': [0, 1, 2, 1, 2],
        'risk_class': [0, 1, 2, 1, 2],
        'ambulances': [1, 5, 10, 2, 7],
        'fire_trucks': [0, 1, 3, 1, 2],
        'rescue_boats': [0, 1, 5, 0, 2]
    })

def test_data_generator_logic():
    # Mock aggregate_real_world_data to avoid network call
    with patch("ml_pipeline.data_generator.aggregate_real_world_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = []
        
        # Mock to_csv to avoid writing real file
        with patch("pandas.DataFrame.to_csv") as mock_to_csv:
            generate_disaster_data(num_samples=100)
            assert mock_to_csv.called

def test_load_data_error():
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = False
        assert load_data() is None

def test_train_severity_model(sample_df):
    with patch("joblib.dump") as mock_dump:
        train_severity_model(sample_df)
        assert mock_dump.called
        # Check path argument of joblib.dump
        args, _ = mock_dump.call_args
        assert "severity_model.joblib" in args[1]

def test_train_resource_model(sample_df):
    with patch("joblib.dump") as mock_dump:
        train_resource_model(sample_df)
        assert mock_dump.called
        args, _ = mock_dump.call_args
        assert "resource_model.joblib" in args[1]

def test_train_risk_model(sample_df):
    with patch("joblib.dump") as mock_dump:
        train_risk_prediction_model(sample_df)
        assert mock_dump.called
        args, _ = mock_dump.call_args
        assert "risk_prediction_model.joblib" in args[1]
