pipeline {
    agent any

    options {
        timestamps()
    }

    environment {
        GIT_CREDENTIALS_ID = 'github-credentials'
        PYTHON_PATH = 'C:\\Users\\HP\\AppData\\Local\\Programs\\Python\\Python310\\python.exe'

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

            // Use native PowerShell, not bat
            powershell """
                \$modelPath = Join-Path '${env.WORKSPACE}' 'Model'
                if (Test-Path \$modelPath) {
                    Remove-Item -Recurse -Force -Path \$modelPath
                    Write-Host '✅ Model folder cleaned up'
                } else {
                    Write-Host '⚠️ Model folder not found, skipping cleanup'
                }
            """

            // Handle model import
            if (params.MODEL_GIT_URL?.trim()) {
                echo "📥 Cloning model from GitHub: ${params.MODEL_GIT_URL}"
                bat "git clone ${params.MODEL_GIT_URL} Model"
            } else if (params.MODEL_LOCAL_PATH?.trim()) {
                echo "📁 Copying model from local path: ${params.MODEL_LOCAL_PATH}"
                bat "xcopy /E /I /Y \"${params.MODEL_LOCAL_PATH}\" \"${env.WORKSPACE}\\Model\""
            } else {
                error "❌ No model source provided! Please provide either MODEL_GIT_URL or MODEL_LOCAL_PATH."
            }
        }
    }
}
stage('Security Scan') {
  steps {
    bat '"C:\\Users\\HP\\AppData\\Local\\Programs\\Python\\Python310\\python.exe" generate_aibom.py --model-path Model\\script --output-dir reports'
    archiveArtifacts artifacts: 'reports/merged_vulnerabilities.json', onlyIfSuccessful: true
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
                    bat """
"${PYTHON_PATH}" "${WORKSPACE}\\Model\\generate_aibom.py" ^
--model-path "${WORKSPACE}\\Model" ^
--output-dir "${REPORT_DIR}"
"""

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
