#!/bin/bash

# Script per configurare il job Jenkins per WebRobot ETL API Documentation
# Basato sull'esperienza con il setup Jenkins precedente

set -e

echo "🚀 SETUP JENKINS JOB PER WEBROBOT ETL API DOC"
echo "============================================="

# Variabili di configurazione
JENKINS_CLI_JAR="${JENKINS_CLI_JAR:-/tmp/jenkins-cli.jar}"
JOB_NAME="webrobot-etl-api-doc-pipeline"
JENKINS_URL="${JENKINS_URL:-http://localhost:8081}"
JENKINS_USER="${JENKINS_USER:-admin}"

# Colori per output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Verifica dipendenze
check_dependencies() {
    log "🔍 Verifica dipendenze..."

    if ! command -v java &> /dev/null; then
        error "Java non trovato. Installalo prima di continuare."
        exit 1
    fi

    if ! command -v curl &> /dev/null; then
        error "curl non trovato."
        exit 1
    fi

    log "✅ Dipendenze OK"
}

# Scarica Jenkins CLI
download_jenkins_cli() {
    log "⬇️ Download Jenkins CLI..."

    if [ ! -f "$JENKINS_CLI_JAR" ]; then
        log "Scaricamento jenkins-cli.jar..."
        if ! curl -s -o "$JENKINS_CLI_JAR" "$JENKINS_URL/jnlpJars/jenkins-cli.jar"; then
            error "Impossibile scaricare Jenkins CLI"
            exit 1
        fi
    else
        log "Jenkins CLI già presente"
    fi

    log "✅ Jenkins CLI pronto"
}

# Test connessione Jenkins
test_jenkins_connection() {
    log "🔗 Test connessione Jenkins..."

    # Verifica che Jenkins sia raggiungibile
    if ! curl -s --max-time 10 "$JENKINS_URL" > /dev/null; then
        error "Jenkins non raggiungibile su $JENKINS_URL"
        echo ""
        echo "💡 Possibili soluzioni:"
        echo "1. Verifica che Jenkins sia in esecuzione"
        echo "2. Controlla il port forwarding: kubectl port-forward -n cicd svc/jenkins 8081:8080"
        echo "3. Verifica JENKINS_URL (default: http://localhost:8081)"
        exit 1
    fi

    log "✅ Jenkins raggiungibile"
}

# Verifica credenziali
check_credentials() {
    log "🔐 Verifica credenziali..."

    # Test connessione con credenziali
    if [ -z "$JENKINS_TOKEN" ]; then
        warning "JENKINS_TOKEN non impostato"
        echo ""
        echo "💡 Come ottenere il token:"
        echo "1. Vai su: $JENKINS_URL/user/$JENKINS_USER/configure"
        echo "2. Clicca 'Add new Token'"
        echo "3. Copia il token generato"
        echo "4. Esporta: export JENKINS_TOKEN=il_tuo_token"
        echo ""
        read -p "Hai il token? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        read -p "Inserisci il token: " JENKINS_TOKEN
        export JENKINS_TOKEN="$JENKINS_TOKEN"
    fi

    log "✅ Credenziali configurate"
}

# Crea il job XML
create_job_xml() {
    log "📝 Creazione configurazione job..."

    cat > /tmp/webrobot-etl-api-doc-job.xml << 'EOF'
<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job@1385.va39f2f9da_8ce">
  <description>WebRobot ETL API Documentation - Build, Docker &amp; Deploy</description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <hudson.model.ParametersDefinitionProperty>
      <parameterDefinitions>
        <hudson.model.ChoiceParameterDefinition>
          <name>BUILD_TYPE</name>
          <description>Tipo di build da eseguire</description>
          <choices class="java.util.Arrays$ArrayList">
            <a class="string-array">
              <string>dev</string>
              <string>staging</string>
              <string>production</string>
            </a>
          </choices>
        </hudson.model.ChoiceParameterDefinition>
        <hudson.model.BooleanParameterDefinition>
          <name>REDEPLOY_ONLY</name>
          <defaultValue>false</defaultValue>
          <description>Salta build e test, esegui solo il deploy K8s</description>
        </hudson.model.BooleanParameterDefinition>
        <hudson.model.BooleanParameterDefinition>
          <name>PUSH_IMAGE</name>
          <defaultValue>true</defaultValue>
          <description>Push dell&apos;immagine Docker su GHCR</description>
        </hudson.model.BooleanParameterDefinition>
        <hudson.model.BooleanParameterDefinition>
          <name>DEPLOY_K8S</name>
          <defaultValue>true</defaultValue>
          <description>Deploy automatico su Kubernetes</description>
        </hudson.model.BooleanParameterDefinition>
      </parameterDefinitions>
    </hudson.model.ParametersDefinitionProperty>
  </properties>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@3894.vd0f0248b_a_fc4">
    <scm class="hudson.plugins.git.GitSCM" plugin="git@5.2.1">
      <configVersion>2</configVersion>
      <userRemoteConfigs>
        <hudson.plugins.git.UserRemoteConfig>
          <url>https://github.com/WebRobot-Ltd/webrobot-etl-api-doc.git</url>
          <credentialsId>github-token</credentialsId>
        </hudson.plugins.git.UserRemoteConfig>
      </userRemoteConfigs>
      <branches>
        <hudson.plugins.git.BranchSpec>
          <name>*/master</name>
        </hudson.plugins.git.BranchSpec>
      </branches>
      <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
      <submoduleCfg class="list"/>
      <extensions/>
    </scm>
    <scriptPath>Jenkinsfile</scriptPath>
    <lightweight>true</lightweight>
  </definition>
  <triggers>
    <hudson.triggers.SCMTrigger>
      <spec>H/5 * * * *</spec>
      <ignorePostCommitHooks>false</ignorePostCommitHooks>
    </hudson.triggers.SCMTrigger>
  </triggers>
  <disabled>false</disabled>
</flow-definition>
EOF

    log "✅ Configurazione job creata"
}

# Crea il job su Jenkins
create_jenkins_job() {
    log "🚀 Creazione job Jenkins..."

    # Comando Jenkins CLI
    JENKINS_CMD="java -jar $JENKINS_CLI_JAR -s $JENKINS_URL -auth $JENKINS_USER:$JENKINS_TOKEN"

    # Verifica se il job esiste già
    if $JENKINS_CMD get-job "$JOB_NAME" > /dev/null 2>&1; then
        warning "Job $JOB_NAME esiste già. Vuoi sovrascriverlo?"
        read -p "Sovrascrivere? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log "Cancellazione job esistente..."
            $JENKINS_CMD delete-job "$JOB_NAME"
        else
            log "Uso del job esistente"
            return
        fi
    fi

    # Crea il nuovo job
    log "Creazione nuovo job: $JOB_NAME"
    $JENKINS_CMD create-job "$JOB_NAME" < /tmp/webrobot-etl-api-doc-job.xml

    if [ $? -eq 0 ]; then
        log "✅ Job creato con successo"
    else
        error "Creazione job fallita"
        exit 1
    fi
}

# Verifica configurazione
verify_setup() {
    log "🔍 Verifica configurazione..."

    JENKINS_CMD="java -jar $JENKINS_CLI_JAR -s $JENKINS_URL -auth $JENKINS_USER:$JENKINS_TOKEN"

    # Lista job
    echo "Job disponibili:"
    $JENKINS_CMD list-jobs

    # Verifica il nostro job
    if $JENKINS_CMD get-job "$JOB_NAME" > /dev/null 2>&1; then
        log "✅ Job $JOB_NAME configurato correttamente"
    else
        error "Job $JOB_NAME non trovato"
        exit 1
    fi
}

# Mostra informazioni finali
show_info() {
    echo ""
    echo "🎉 SETUP COMPLETATO!"
    echo ""
    echo "📊 INFORMAZIONI JOB:"
    echo "==================="
    echo ""
    echo "🏷️  Job Name: $JOB_NAME"
    echo "🌐 Jenkins URL: $JENKINS_URL"
    echo "📁 Repository: https://github.com/WebRobot-Ltd/webrobot-etl-api-doc"
    echo "📂 Script Path: Jenkinsfile"
    echo ""
    echo "⚙️  Parametri configurati:"
    echo "   - BUILD_TYPE (dev/staging/production)"
    echo "   - REDEPLOY_ONLY (solo redeploy)"
    echo "   - PUSH_IMAGE (push su GHCR)"
    echo "   - DEPLOY_K8S (deploy su Kubernetes)"
    echo ""
    echo "🚀 Come utilizzare:"
    echo "1. Vai su: $JENKINS_URL/job/$JOB_NAME"
    echo "2. Clicca 'Build with Parameters'"
    echo "3. Configura i parametri desiderati"
    echo "4. Clicca 'Build'"
    echo ""
    echo "⏰ Trigger automatici:"
    echo "   - Push su branch master (ogni 5 minuti)"
    echo "   - Webhook GitHub (se configurato)"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   - Logs: $JENKINS_URL/job/$JOB_NAME/lastBuild/console"
    echo "   - Status: $JENKINS_URL/job/$JOB_NAME"
    echo ""
}

# Main execution
main() {
    echo ""
    echo "🎯 OBIETTIVO: Configurare job Jenkins per WebRobot ETL API Documentation"
    echo ""

    check_dependencies
    download_jenkins_cli
    test_jenkins_connection
    check_credentials
    create_job_xml
    create_jenkins_job
    verify_setup
    show_info
}

# Esegui main se script chiamato direttamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main
fi

