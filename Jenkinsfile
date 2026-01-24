
pipeline {
    agent any

    options { timestamps() }

    environment {
        // --- CONFIGURE THIS ONE THING ---
        // If JS project is at repo root -> leave as empty string ''
        // If in a folder, put the exact folder name (quotes kept), e.g.:
        // JS_DIR = 'playwright-js \\ automation playwright task'
        JS_DIR = ''

        // Python locations
        VENV_DIR      = 'venv'
        PY_TEST_PATH  = 'playwright-python/DemoWebShop/tests'
        PY_ALLURE_DIR = 'allure-results'
        TEST_REPORT   = 'report.html'

        // JS Allure results (directory will be created in the JS working dir)
        JS_ALLURE_DIR = 'allure-results-js'

        // Browser cache (skip re-downloads)
        PLAYWRIGHT_BROWSERS_PATH            = 'C:\\ms-playwright'
        PLAYWRIGHT_BROWSER_DOWNLOAD_TIMEOUT = '600000'  // 10 minutes
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Diag: locate JS project (one-time)') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"
                    Write-Host "Repo root contents:"
                    Get-ChildItem -Force | Select-Object Name,Mode,Length

                    Write-Host "`nSearch for package.json:"
                    Get-ChildItem -Recurse -Filter package.json | Select-Object -Expand FullName

                    Write-Host "`nSearch for playwright.config.js:"
                    Get-ChildItem -Recurse -Filter playwright.config.js | Select-Object -Expand FullName
                '''
            }
        }

        /* ====================== JavaScript Playwright ====================== */
        stage('Check Node & npm') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"
                    node -v
                    npm -v
                '''
            }
        }

        stage('Install Node deps (JS)') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    # Resolve JS working directory
                    $jsDir = $env:JS_DIR
                    if ([string]::IsNullOrWhiteSpace($jsDir)) { $jsDir = '.' }

                    # Preflight checks
                    $pkg = Join-Path $jsDir 'package.json'
                    $cfg = Join-Path $jsDir 'playwright.config.js'
                    if (!(Test-Path $pkg)) { Write-Error "package.json not found at: $pkg. Set JS_DIR correctly ('' for root or exact folder name)."; exit 1 }
                    if (!(Test-Path $cfg)) { Write-Error "playwright.config.js not found at: $cfg. Set JS_DIR correctly."; exit 1 }

                    Push-Location $jsDir
                    try {
                        if (Test-Path 'package-lock.json') { npm ci } else { npm install }
                        npx playwright install chromium
                    } finally {
                        Pop-Location
                    }
                '''
            }
        }

        stage('Run JS Playwright (Allure)') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    # Resolve JS working directory
                    $jsDir = $env:JS_DIR
                    if ([string]::IsNullOrWhiteSpace($jsDir)) { $jsDir = '.' }

                    $cfg = Join-Path $jsDir 'playwright.config.js'
                    if (!(Test-Path $cfg)) { Write-Error "playwright.config.js not found at: $cfg. Cannot run JS tests."; exit 1 }

                    Push-Location $jsDir
                    try {
                        # Clean previous JS Allure results in JS dir
                        if (Test-Path ".\\$($env:JS_ALLURE_DIR)") { Remove-Item -Recurse -Force ".\\$($env:JS_ALLURE_DIR)" }

                        # Run JS tests using the config in JS dir
                        npx playwright test --config=playwright.config.js
                    } finally {
                        Pop-Location
                    }
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
                retry(2) {
                    powershell '''
                        $ErrorActionPreference = "Stop"
                        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
                        . ".\\${env:VENV_DIR}\\Scripts\\Activate.ps1"

                        if (!(Test-Path "${env:PLAYWRIGHT_BROWSERS_PATH}")) {
                            New-Item -ItemType Directory -Path "${env:PLAYWRIGHT_BROWSERS_PATH}" | Out-Null
                        }

                        # Windows: no --with-deps
                        python -m playwright install chromium
                    '''
                }
            }
        }

        stage('Run Python Tests (Allure + HTML)') {
            steps {
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
            // Resolve JS results path relative to workspace
            script {
                // Groovy side build of JS allure path for the publisher
                def jsDir = env.JS_DIR?.trim()
                if (!jsDir) {
                    env.JS_ALLURE_PUBLISH = "${env.JS_ALLURE_DIR}"
                } else {
                    env.JS_ALLURE_PUBLISH = "${jsDir}/${env.JS_ALLURE_DIR}"
                }
            }

            // Publish combined Allure report (Python + JS)
            allure includeProperties: false, jdk: '',
                   results: [
                       [path: 'allure-results'],                // Python
                       [path: "${env.JS_ALLURE_PUBLISH}"]       // JavaScript (root or subfolder)
                   ]

            // Archive raw artifacts
            archiveArtifacts artifacts: "report.html, artifacts/**, allure-results/**, ${env.JS_ALLURE_PUBLISH}/**",
                             fingerprint: true,
                             allowEmptyArchive: true

            echo "Reports published (JS + Python). JS results dir: ${env.JS_ALLURE_PUBLISH}"
        }
        unstable {
            echo 'Build UNSTABLE due to test failures.'
        }
        failure {
            echo 'Build FAILED at pipeline level.'
        }
    }
}
