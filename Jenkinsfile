pipeline {
    agent any

    stages {

        stage('Setup') {
            steps {
                powershell '''
                    python -m venv venv
                    .\\venv\\Scripts\\python -m pip install --upgrade pip
                    .\\venv\\Scripts\\python -m pip install -r requirements.txt
                    .\\venv\\Scripts\\python -m playwright install chromium
                '''
            }
        }

        stage('Run Tests') {
            steps {
                powershell '''
                    .\\venv\\Scripts\\python -m pytest --html=report.html --self-contained-html
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts 'report.html'
        }
    }
}