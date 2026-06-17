pipeline {
    agent any

    parameters {
        choice(name: 'ENV', choices: ['UAT'], description: 'Target environment')
        choice(name: 'APP', choices: ['efms', 'etms', 'all'], description: 'Application filter')
        choice(name: 'BROWSER', choices: ['chrome', 'edge'], description: 'Browser channel')
        choice(name: 'HEADLESS', choices: ['true', 'false'], description: 'Run browser in headless mode')
        choice(
            name: 'MARKER',
            choices: ['critical', 'high', 'login', 'navigation', 'smoke', 'regression', 'efms', 'etms'],
            description: 'Pytest marker (efms/etms = full app suite)'
        )
        string(name: 'EFMS_ACCOUNT_USERNAME', defaultValue: 'QCTest', description: 'eFMS login username')
        string(name: 'ETMS_ACCOUNT_USERNAME', defaultValue: 'automation.test', description: 'eTMS login username')
        string(name: 'PYTEST_ARGS', defaultValue: '', description: 'Extra pytest arguments')
    }

    environment {
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
        UV_CACHE_DIR = '.uv-cache'
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Install') {
            steps {
                sh '''
                    python3 -m pip install --user uv
                    export PATH="$HOME/.local/bin:$PATH"
                    uv sync --extra dev
                    uv run playwright install --with-deps ${BROWSER}
                '''
            }
        }

        stage('Quality') {
            steps {
                sh '''
                    export PATH="$HOME/.local/bin:$PATH"
                    uv run ruff check .
                    uv run ruff format --check .
                    uv run pyright
                '''
            }
        }

        stage('Run Tests') {
            steps {
                withCredentials([
                    string(credentialsId: 'automation-efms-account-password', variable: 'EFMS_ACCOUNT_PASSWORD'),
                    string(credentialsId: 'automation-etms-account-password', variable: 'ETMS_ACCOUNT_PASSWORD'),
                ]) {
                    sh '''
                        export PATH="$HOME/.local/bin:$PATH"
                        export ENV=${ENV}
                        export APP=${APP}
                        export MARKER=${MARKER}
                        export BROWSER=${BROWSER}
                        export HEADLESS=${HEADLESS}
                        export EFMS_ACCOUNT_USERNAME=${EFMS_ACCOUNT_USERNAME}
                        export ETMS_ACCOUNT_USERNAME=${ETMS_ACCOUNT_USERNAME}
                        export PYTEST_ARGS="${PYTEST_ARGS}"
                        bash scripts/ci-run-tests.sh
                    '''
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**/*,test-results/**/*,logs/**/*', allowEmptyArchive: true
        }
    }
}
