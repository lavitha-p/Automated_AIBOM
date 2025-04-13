pipeline {
    agent any

    environment {
        GIT_CREDENTIALS_ID = 'github-credentials'
        PYTHON_PATH = 'C:\Users\HP\AppData\Local\Programs\Python\Python310\python.exe'
        MODEL_DIR = "${WORKSPACE}\\Model"
        SCRIPT_REPO = 'https://github.com/lavitha-p/Automated_AIBOM.git'
        TOOLS_DIR = "${MODEL_DIR}\\tools"
        TIMESTAMP = "${new Date().format('yyyyMMdd_HHmmss')}"
        REPORT_DIR = "${WORKSPACE}\\reports_${TIMESTAMP}"
    }

    parameters {
        string(name: 'MODEL_GIT_URL', defaultValue: '', description: 'Enter GitHub repo URL for the model (leave empty if using local path)')
        string(name: 'MODEL_LOCAL_PATH', defaultValue: '', description: 'Enter local model path (leave empty if using GitHub)')
    }

    stages {
        stage('Build') {
            steps {
                script {
                    echo "🔥 Force cleanup of Model folder..."
                   bat "powershell -Command \"Remove-Item -Recurse -Force -Path '${env.MODEL_DIR}' -ErrorAction SilentlyContinue\""


                    echo "📥 Cloning model from GitHub: ${params.MODEL_GIT_URL}"
                    bat """git clone ${params.MODEL_GIT_URL} "${MODEL_DIR}" """

                    echo "🧾 Copying dataset and model info files into model directory..."
                    bat """copy "${env.WORKSPACE}\\dataset.json" "${MODEL_DIR}\\dataset.json" """
                    bat """copy "${env.WORKSPACE}\\model_info.json" "${MODEL_DIR}\\model_info.json" """

                    if (!fileExists("${MODEL_DIR}\\dataset.json") || !fileExists("${MODEL_DIR}\\model_info.json")) {
                        error "❌ Required files dataset.json or model_info.json not found!"
                    }

                    echo "✅ Build stage completed."
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    echo "📥 Fetching AIBOM script..."
                    bat """git clone ${SCRIPT_REPO} "${MODEL_DIR}\\script" """
                    bat """copy "${MODEL_DIR}\\script\\generate_aibom.py" "${MODEL_DIR}\\" """
                    echo "✅ Deploy stage completed."
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    echo "🧰 Installing Syft and Trivy..."

                    bat """mkdir "${TOOLS_DIR}" """

                    powershell '''
                    $toolsDir = "${env:TOOLS_DIR}"
                    $syftExe = Join-Path $toolsDir "syft.exe"
                    $trivyZip = Join-Path $toolsDir "trivy.zip"
                    $trivyDir = Join-Path $toolsDir "trivy"
                    $trivyExe = Join-Path $trivyDir "trivy.exe"

                    curl.exe -L -o $syftExe "https://github.com/anchore/syft/releases/download/v1.2.0/syft_1.2.0_windows_amd64.exe"
                    curl.exe -L -o $trivyZip "https://github.com/aquasecurity/trivy/releases/download/v0.51.1/trivy_0.51.1_Windows-64bit.zip"
                    Expand-Archive -Path $trivyZip -DestinationPath $trivyDir -Force

                    $env:PATH += ";$toolsDir;$trivyDir"
                    Write-Host "✅ Syft and Trivy installed."
                    '''

                    echo "📦 Installing Python dependencies..."
                    bat """ "${env.PYTHON_PATH}" -m pip install --upgrade pip """
                    bat """ "${env.PYTHON_PATH}" -m pip install psutil pandas torch tensorflow """

                    echo "📁 Creating report folder: ${REPORT_DIR}"
                    bat """mkdir "${REPORT_DIR}" """

                    echo "🚀 Running AIBOM generator..."
                    bat """ "${env.PYTHON_PATH}" "${MODEL_DIR}\\generate_aibom.py" --dataset "${MODEL_DIR}\\dataset.json" --modelinfo "${MODEL_DIR}\\model_info.json" --modelfile "${MODEL_DIR}\\model.pt" """

                    echo "✅ Test stage completed."
                }
            }
        }

        stage('Promote') {
            steps {
                script {
                    def vulnReportPath = "${REPORT_DIR}\\vulnerability_report.json"
                    def aibomPath = "${REPORT_DIR}\\aibom.json"
                    def sbomPath = "${REPORT_DIR}\\sbom.json"
                    def auditPath = "${REPORT_DIR}\\audit_log.json"

                    def aibomExists = fileExists(aibomPath)
                    def sbomExists = fileExists(sbomPath)
                    def vulnExists = fileExists(vulnReportPath)

                    if (aibomExists && sbomExists && vulnExists) {
                        def vulnReport = readFile(vulnReportPath)
                        if (vulnReport =~ /LOW|MEDIUM|HIGH|CRITICAL/) {
                            echo "⚠️ WARNING: Model has vulnerabilities! Review required before promotion."
                        } else {
                            echo "✅ Model passes all security checks. Good to promote."
                        }
                    } else {
                        echo "⚠️ One or more reports are missing. Manual review needed."
                    }

                    echo "📢 Reports saved to: ${REPORT_DIR}"
                    echo "🧾 Audit Summary:"
                    if (fileExists(auditPath)) {
                        echo readFile(auditPath)
                    }

                    echo "✅ Promote stage completed."
                }
            }
        }
    }

    post {
        failure {
            echo "❌ Pipeline failed. Check logs and reports in ${REPORT_DIR}."
        }
        success {
            echo "✅ Pipeline executed successfully! All reports are in: ${REPORT_DIR}"
        }
    }
}
