
pipeline {
    agent any

    options { timestamps() }

    environment {
        VENV_DIR    = 'venv'
        TEST_REPORT = 'report.html'
        ALLURE_DIR  = 'allure-results'
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Set up Python venv') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"
                    python --version

                    if (!(Test-Path ".\\${env:VENV_DIR}")) {
                        python -m venv "${env:VENV_DIR}"
                    }

                    . ".\\${env:VENV_DIR}\\Scripts\\Activate.ps1"
                    python -m pip install --upgrade pip

                    if (Test-Path ".\\requirements.txt") {
                        pip install -r requirements.txt
                    } else {
                        Write-Warning "requirements.txt not found at repo root"
                        pip install pytest pytest-html playwright pytest-playwright allure-pytest
                    }

                    python -m playwright install --with-deps
                '''
            }
        }

        stage('Run Tests (with Allure)') {
            steps {
                // Mark the stage FAILURE but keep the build UNSTABLE so Allure can publish
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    powershell '''
                        $ErrorActionPreference = "Stop"
                        . ".\\${env:VENV_DIR}\\Scripts\\Activate.ps1"

                        if (!(Test-Path ".\\artifacts")) { New-Item -ItemType Directory -Path ".\\artifacts" | Out-Null }
                        if (!(Test-Path ".\\${env:ALLURE_DIR}")) { New-Item -ItemType Directory -Path ".\\${env:ALLURE_DIR}" | Out-Null }

                        pytest -q --maxfail=1 --disable-warnings `
                          --html="${env:TEST_REPORT}" --self-contained-html `
                          --alluredir="${env:ALLURE_DIR}" `
                          --tracing=retain-on-failure `
                          --screenshot=only-on-failure `
                          --video=retain-on-failure `
                          --output=artifacts/playwright
                    '''
                }
            }
        }
    }

    post {
        always {
            // Publish Allure report (requires Allure Jenkins Plugin + configured Allure commandline)
            allure includeProperties: false, jdk: '', results: [[path: 'allure-results']]

            // Keep raw artifacts (HTML report + Playwright outputs)
            archiveArtifacts artifacts: 'report.html, artifacts/**, allure-results/**', fingerprint: true, allowEmptyArchive: true
        }
        unstable {
            echo 'Build marked UNSTABLE due to test failures. Allure report published.'
        }
        failure {
            echo 'Build FAILED at pipeline level.'
        }
    }
}
