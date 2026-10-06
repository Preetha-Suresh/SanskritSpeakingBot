pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code from GitHub...'
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo 'Installing Python dependencies...'
                bat 'python --version'
                bat 'pip install -r requirements.txt'
            }
        }

        stage('Test/Validate') {
            steps {
                echo 'Validating Python application...'
                bat 'python -m py_compile main.py'
                echo 'Python syntax validation successful.'
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker image...'
                bat 'docker build -t sanskrit-speaking-bot:1.0 .'
            }
        }
    }

    post {

        success {
            echo '======================================'
            echo 'PIPELINE SUCCESSFUL'
            echo 'Sanskrit Speaking Bot Docker image created.'
            echo '======================================'
        }

        failure {
            echo '======================================'
            echo 'PIPELINE FAILED'
            echo 'Check the Jenkins console output.'
            echo '======================================'
        }
    }
}