pipeline {
  agent { label 'linux-docker-java17' }
  options { timestamps(); timeout(time: 60, unit: 'MINUTES'); disableConcurrentBuilds(); buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '5')) }
  triggers { cron('TZ=Asia/Kolkata\n0 1 * * *') }
  parameters { string(name: 'TAGS', defaultValue: '@smoke', description: 'Cucumber tag expression') }
  environment { TEST_TAGS = "${params.TAGS}" }
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Java and runtime') { steps { sh 'java -version'; sh 'docker compose version'; sh 'python3 --version'; sh 'chmod +x mvnw' } }
    stage('Provision and test') {
      steps {
        withCredentials([string(credentialsId: 'orangehrm-qa-admin-password', variable: 'ADMIN_SECRET')]) {
          sh '''
            set +x
            cp .env.example .env
            python3 - <<'PY'
import os,secrets
from pathlib import Path
values={'ADMIN_PASSWORD':os.environ['ADMIN_SECRET'],'MYSQL_ROOT_PASSWORD':secrets.token_hex(24),'MYSQL_PASSWORD':secrets.token_hex(24),'DB_PASSWORD':secrets.token_hex(24)}
Path('.env').write_text('\\n'.join(k+'='+values.get(k,v) for k,v in (line.split('=',1) for line in Path('.env').read_text().splitlines()))+'\\n')
PY
            bash scripts/ci.sh
          '''
        }
      }
    }
  }
  post {
    always {
      archiveArtifacts artifacts: 'target/allure-results/**,target/site/allure-maven-plugin/**,target/surefire-reports/**,target/cucumber.json', allowEmptyArchive: true
      sh 'docker compose down --volumes --remove-orphans'
      sh 'rm -f .env'
    }
  }
}
