pipeline {
    agent any

    parameters {
        choice(name: 'ENV', choices: ['UAT'], description: 'Target environment')
        choice(name: 'BROWSER', choices: ['chrome', 'edge'], description: 'Browser channel')
        choice(name: 'HEADLESS', choices: ['true', 'false'], description: 'Run browser in headless mode')
        choice(name: 'MARKER', choices: ['critical', 'high', 'login', 'navigation', 'smoke', 'regression'], description: 'Pytest marker')
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
                    uv run playwright install --with-deps chrome msedge
                '''
            }
        }

        stage('Quality') {
            steps {
                sh '''
                    export PATH="$HOME/.local/bin:$PATH"
                    uv run ruff check .
                    uv run pyright
                '''
            }
        }

        stage('Run Tests') {
            steps {
                withCredentials([string(credentialsId: 'automation-account-password', variable: 'ACCOUNT_PASSWORD')]) {
                    sh '''
                        export PATH="$HOME/.local/bin:$PATH"
                        ENV=${ENV} BROWSER=${BROWSER} BROWSER_HEADLESS=${HEADLESS} \
                        uv run pytest -m ${MARKER} \
                          --html=reports/report.html \
                          --self-contained-html \
                          ${PYTEST_ARGS}
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
