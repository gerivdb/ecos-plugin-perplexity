# Cahier des Charges - Paramètres Métier
# Configuration YAML pour Espace Perplexity AI avec Simili-Programmation Python

# ===================================================================
# CONFIGURATION GÉNÉRALE ENVIRONNEMENT
# ===================================================================

environment:
  name: "production"  # dev, staging, production
  version: "2.1.0"
  deployment_date: "2025-09-02T21:00:00Z"
  
# ===================================================================  
# PARAMÈTRES DE SÉCURITÉ ET AUTHENTIFICATION
# ===================================================================

security:
  authentication:
    method: "sso_saml"  # sso_saml, oauth2, local
    sso_provider: "azure_ad"
    session_timeout: 28800  # 8 heures en secondes
    mfa_required_roles: ["admin", "security_officer"]
    password_policy:
      min_length: 12
      require_special_chars: true
      require_numbers: true
      expiry_days: 90
      
  authorization:
    rbac_enabled: true
    default_role: "user_metier"
    roles:
      user_metier:
        permissions: ["execute_approved_scripts", "read_configs", "create_reports"]
        resource_limits:
          cpu_cores: 1
          memory_mb: 512
          timeout_seconds: 30
          concurrent_scripts: 2
          
      expert_metier:
        permissions: ["create_scripts", "modify_configs", "manage_workflows"]
        resource_limits:
          cpu_cores: 2
          memory_mb: 2048
          timeout_seconds: 300
          concurrent_scripts: 5
          
      admin:
        permissions: ["all"]
        resource_limits:
          cpu_cores: 4
          memory_mb: 8192
          timeout_seconds: 1800
          concurrent_scripts: 10
          
  sandbox:
    python_version: "3.11"
    isolation_level: "container"  # container, vm, process
    network_access: "restricted"  # none, restricted, full
    allowed_imports:
      - "pandas"
      - "numpy" 
      - "requests"
      - "json"
      - "datetime"
      - "re"
      - "math"
      - "statistics"
      - "plotly"
      - "matplotlib"
      - "seaborn"
    blocked_imports:
      - "os"
      - "subprocess"
      - "sys"
      - "importlib"
      - "eval"
      - "exec"

# ===================================================================
# CONFIGURATION SOURCES EXTERNES ET APIs
# ===================================================================

external_sources:
  web_scraping:
    enabled: true
    rate_limiting:
      requests_per_minute: 60
      concurrent_requests: 5
    user_agent: "PerplexityAI-MetierSpace/2.1 (contact@company.com)"
    respect_robots_txt: true
    cache_strategy:
      default_ttl: 3600  # 1 heure
      max_cache_size_mb: 1024
      
  trusted_sources:
    pricing_data:
      - url: "https://api.pricingprovider.com"
        auth_type: "api_key"
        reliability_score: 95
        cache_ttl: 300  # 5 minutes pour données temps réel
        
    market_data:
      - url: "https://api.marketdata.com"
        auth_type: "oauth2"
        reliability_score: 90
        cache_ttl: 1800  # 30 minutes
        
    booking_apis:
      - url: "https://api.booking.com/partner"
        auth_type: "api_key"
        reliability_score: 98
        cache_ttl: 60  # 1 minute disponibilités
        
  api_management:
    timeout_seconds: 30
    retry_attempts: 3
    retry_backoff: "exponential"  # linear, exponential
    circuit_breaker:
      failure_threshold: 5
      recovery_timeout: 300
      
# ===================================================================
# RÈGLES MÉTIER SPÉCIALISÉES
# ===================================================================

business_rules:
  comparateur_prix:
    monitoring:
      check_frequency: "*/15 * * * *"  # Cron: toutes les 15 minutes
      price_variation_alert_threshold: 5.0  # Pourcentage
      competitors_to_track: 10
      categories:
        - "electronics"
        - "fashion" 
        - "home_garden"
      
    calculation_rules:
      pricing_algorithm: "dynamic_competitive"
      factors:
        demand_weight: 0.4
        competition_weight: 0.3
        seasonality_weight: 0.2
        inventory_weight: 0.1
      price_bounds:
        min_margin_percent: 10
        max_markup_percent: 200
        
  booking_agence:
    availability:
      real_time_check: true
      overbooking_threshold: 3  # Pourcentage autorisé
      cache_duration_minutes: 2
      
    pricing:
      dynamic_pricing: true
      peak_season_multiplier: 1.5
      last_minute_discount_percent: 20
      cancellation_policy: "flexible"  # strict, moderate, flexible
      
    workflow:
      auto_confirmation_limit: 500  # EUR, au-delà validation manuelle
      payment_methods: ["card", "paypal", "bank_transfer"]
      confirmation_email_template: "booking_confirmation_v2"
      
  groupe_musique:
    production:
      stages:
        - "brief_analysis"
        - "concept_generation" 
        - "resource_planning"
        - "production_tracking"
        - "quality_validation"
        - "distribution"
        
      automation:
        trend_analysis_sources:
          - "spotify_charts"
          - "youtube_trending" 
          - "social_media_apis"
        budget_estimation_model: "ml_regression_v3"
        resource_optimization: "constraint_solver"
        
    distribution:
      platforms:
        - name: "youtube"
          api_endpoint: "https://www.googleapis.com/youtube/v3"
          auto_upload: true
        - name: "spotify"  
          api_endpoint: "https://api.spotify.com/v1"
          auto_upload: false  # Validation manuelle requise
          
# ===================================================================
# CONFIGURATION MONITORING ET ALERTING
# ===================================================================

monitoring:
  metrics:
    system:
      - "cpu_usage"
      - "memory_usage"
      - "disk_usage"
      - "network_io"
      - "response_time"
      
    business:
      - "user_satisfaction_score"
      - "script_execution_success_rate"
      - "api_call_success_rate"
      - "time_to_insight"
      - "roi_per_feature"
      
  alerting:
    channels:
      email:
        enabled: true
        smtp_server: "smtp.company.com"
        recipients: ["admin@company.com", "ops@company.com"]
        
      slack:
        enabled: true
        webhook_url: "https://hooks.slack.com/services/xxx"
        channel: "#perplexity-alerts"
        
      webhooks:
        enabled: true
        endpoints:
          - "https://monitoring.company.com/webhooks/perplexity"
          
    rules:
      critical:
        - condition: "system.cpu_usage > 90"
          duration: "5m"
          action: "immediate_alert"
          
        - condition: "business.api_success_rate < 95"
          duration: "10m" 
          action: "escalate_to_oncall"
          
      warning:
        - condition: "system.memory_usage > 80"
          duration: "15m"
          action: "notify_team"

# ===================================================================
# CONFIGURATION PERFORMANCE ET SCALABILITÉ  
# ===================================================================

performance:
  caching:
    strategy: "multi_level"  # none, simple, multi_level
    levels:
      - type: "memory"
        size_mb: 256
        ttl_seconds: 300
        
      - type: "redis" 
        size_mb: 2048
        ttl_seconds: 3600
        cluster_nodes: ["redis-1:6379", "redis-2:6379"]
        
  database:
    connection_pool:
      min_connections: 5
      max_connections: 50
      connection_timeout: 30
      
    query_optimization:
      enable_query_cache: true
      slow_query_threshold: 1000  # millisecondes
      explain_analyze_auto: true
      
  compute:
    auto_scaling:
      enabled: true
      min_instances: 2
      max_instances: 10
      scale_up_threshold: 70  # CPU pourcentage
      scale_down_threshold: 30
      
# ===================================================================
# CONFIGURATION DÉVELOPPEMENT ET DÉPLOIEMENT
# ===================================================================

development:
  ci_cd:
    pipeline_trigger: "git_push"  # git_push, manual, scheduled
    environments: ["dev", "staging", "prod"]
    
    testing:
      unit_tests: true
      integration_tests: true
      performance_tests: true
      security_tests: true
      min_coverage_percent: 85
      
    deployment:
      strategy: "blue_green"  # rolling, blue_green, canary
      rollback_enabled: true
      health_check_endpoint: "/health"
      
  feature_flags:
    enabled: true
    provider: "launchdarkly"  # launchdarkly, internal, disabled
    flags:
      ai_code_assistant: false
      advanced_analytics: true
      mobile_app_integration: false
      
# ===================================================================
# TEMPLATES ET STANDARDS DE CONFIGURATION
# ===================================================================

templates:
  user_story:
    format: "En tant que [persona], je veux [action], afin de [bénéfice]"
    required_fields: ["persona", "action", "benefit", "acceptance_criteria"]
    
  script_metadata:
    required_fields:
      - "name"
      - "description" 
      - "author"
      - "version"
      - "dependencies"
      - "resource_requirements"
      - "test_cases"
      
  api_response:
    standard_format: "json"
    required_fields: ["status", "data", "timestamp", "request_id"]
    error_format:
      required_fields: ["error_code", "error_message", "details", "timestamp"]
      
# ===================================================================
# CONFIGURATIONS SPÉCIFIQUES ENVIRONNEMENTS
# ===================================================================

environments:
  development:
    debug_mode: true
    log_level: "DEBUG"
    mock_external_apis: true
    database_url: "postgresql://dev_user:dev_pass@dev-db:5432/perplexity_dev"
    
  staging:
    debug_mode: false
    log_level: "INFO"
    mock_external_apis: false
    database_url: "postgresql://stage_user:stage_pass@stage-db:5432/perplexity_stage"
    performance_monitoring: true
    
  production:
    debug_mode: false
    log_level: "WARNING"
    mock_external_apis: false
    database_url: "${DATABASE_URL}"  # Variable d'environnement sécurisée
    performance_monitoring: true
    security_monitoring: true
    backup_enabled: true
    
# ===================================================================
# CONFIGURATION COMPLIANCE ET AUDIT
# ===================================================================

compliance:
  gdpr:
    enabled: true
    data_retention_days: 2555  # 7 ans
    consent_management: true
    right_to_be_forgotten: true
    data_portability: true
    
  audit:
    enabled: true
    log_all_actions: true
    retention_years: 7
    encryption_at_rest: true
    encryption_in_transit: true
    
  industry_specific:
    finance:
      mifid_compliance: false
      pci_dss_level: 0  # 0=disabled, 1-4=levels
      
    healthcare: 
      hipaa_compliance: false
      
    government:
      fedramp_compliance: false

# ===================================================================
# MÉTRIQUES ET KPIs CONFIGURATION
# ===================================================================

kpis:
  business:
    targets:
      user_adoption_rate: 80  # Pourcentage utilisateurs actifs
      time_to_value_days: 7   # Délai avant première valeur métier
      roi_percent: 200        # ROI attendu sur 12 mois
      satisfaction_score: 4.0 # Score satisfaction sur 5
      
  technical:
    sla:
      availability_percent: 99.5
      response_time_ms: 500
      throughput_rps: 1000   # Requests per second
      error_rate_percent: 0.5
      
  operational:
    targets:
      deployment_frequency: "weekly"
      lead_time_hours: 24
      recovery_time_minutes: 60
      change_failure_rate_percent: 5

# ===================================================================
# INTÉGRATIONS FUTURES ET ROADMAP
# ===================================================================

roadmap:
  next_quarter:
    features:
      - "ai_code_assistant"
      - "mobile_app"
      - "advanced_ml_models"
      - "real_time_collaboration"
      
  integrations:
    planned:
      - name: "salesforce"
        priority: "high" 
        estimated_effort_weeks: 4
        
      - name: "microsoft_teams"
        priority: "medium"
        estimated_effort_weeks: 2
        
      - name: "tableau"
        priority: "low"
        estimated_effort_weeks: 6