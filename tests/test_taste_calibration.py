from creative.reasoning.judge_calibration import calibrate_judge


def test_calibrate_judge_synthetic():
    corr, details = calibrate_judge(n=5)
    # With synthetic labels closely derived from judge, correlation should be high
    assert corr >= 0.9
