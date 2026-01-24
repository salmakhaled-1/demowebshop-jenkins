
pipeline {
    agent any

    options { timestamps() }

    environment {
        // Python
        VENV_DIR      = 'venv'
        PY_TEST_PATH  = 'playwright-python/DemoWebShop/tests'
        PY_ALLURE_DIR = 'allure-results'
        TEST_REPORT   = 'report.html'

        // JavaScript (kept at repo root)
        JS_ALLURE_DIR = 'allure-results-js'

        // Cache Playwright browsers to avoid re-downloading every time
        PLAYWRIGHT_BROWSERS_PATH            = 'C:\\ms-playwright'
        PLAYWRIGHT_BROWSER_DOWNLOAD_TIMEOUT = '600000'  // 10 minutes
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        /* ====================== JavaScript Playwright (ROOT) ====================== */
        stage('Check Node & npm') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"
                    node -v
                    npm -v
                '''
            }
        }

        stage('Install Node deps (JS @ ROOT)') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"
                    # We are at repo root where package.json exists
                    if (Test-Path package-lock.json) { npm ci } else { npm install }

                    # Install browsers (reuses the cached path set in env)
                    npx playwright install chromium
                '''
            }
        }

        stage('Run JS Playwright (Allure @ ROOT)') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    # Clean previous JS Allure results at root
                    if (Test-Path ".\\${env:JS_ALLURE_DIR}") { Remove-Item -Recurse -Force ".\\${env:JS_ALLURE_DIR}" }

                    # Reporter is configured in root playwright.config.js → writes to allure-results-js
                    npx playwright test --config=playwright.config.js
                '''
            }
        }

        /* ====================== Python Playwright ====================== */
        stage('Set up Python venv & deps') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"
                    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force

                    python --version

                    if (!(Test-Path ".\\${env:VENV_DIR}")) {
                        python -m venv "${env:VENV_DIR}"
                    }

                    . ".\\${env:VENV_DIR}\\Scripts\\Activate.ps1"
                    python -m pip install --upgrade pip wheel setuptools

                    if (Test-Path ".\\requirements.txt") {
                        Write-Host "requirements.txt found. Installing..."
                        pip install -r requirements.txt
                    } else {
                        Write-Warning "requirements.txt not found. Installing minimal deps."
                        pip install pytest pytest-html playwright pytest-playwright allure-pytest
                    }
                '''
            }
        }

        stage('Install Playwright browser(s) for Python') {
            steps {
                // Retry to tolerate flaky network
                retry(2) {
                    powershell '''
                        $ErrorActionPreference = "Stop"
                        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
                        . ".\\${env:VENV_DIR}\\Scripts\\Activate.ps1"

                        if (!(Test-Path "${env:PLAYWRIGHT_BROWSERS_PATH}")) {
                            New-Item -ItemType Directory -Path "${env:PLAYWRIGHT_BROWSERS_PATH}" | Out-Null
                        }

                        # Windows: do NOT use --with-deps (Linux-only)
                        python -m playwright install chromium
                    '''
                }
            }
        }

        stage('Run Python Tests (Allure + HTML)') {
            steps {
                // Keep build UNSTABLE on test failures so reports still publish
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    powershell '''
                        $ErrorActionPreference = "Stop"
                        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
                        . ".\\${env:VENV_DIR}\\Scripts\\Activate.ps1"

                        if (!(Test-Path ".\\artifacts"))            { New-Item -ItemType Directory -Path ".\\artifacts" | Out-Null }
                        if (!(Test-Path ".\\${env:PY_ALLURE_DIR}")) { New-Item -ItemType Directory -Path ".\\${env:PY_ALLURE_DIR}" | Out-Null }

                        pytest "${env:PY_TEST_PATH}" -q --disable-warnings `
                          --html="${env:TEST_REPORT}" --self-contained-html `
                          --alluredir="${env:PY_ALLURE_DIR}" `
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
            // Publish ONE Allure report that merges BOTH result folders (root)
            allure includeProperties: false, jdk: '',
                   results: [
                       [path: 'allure-results'],     // Python
                       [path: 'allure-results-js']   // JavaScript
                   ]

            // Keep raw artifacts
            archiveArtifacts artifacts: 'report.html, artifacts/**, allure-results/**, allure-results-js/**',
                             fingerprint: true,
                             allowEmptyArchive: true

            echo 'Reports published (JS + Python) in one Allure report.'
        }
        unstable {
            echo 'Build UNSTABLE due to test failures. Reports published.'
        }
        failure {
            echo 'Build FAILED at pipeline level.'
        }
    }
}
