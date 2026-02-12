// ============================================
// ENHANCED FEATURES - Additional Functions
// ============================================

// Agent Details Toggle
function toggleAgentDetails(agentName) {
  const details = document.getElementById(`details-${agentName}`);
  const icon = document.getElementById(`icon-${agentName}`);
  const btnText = document.getElementById(`btn-text-${agentName}`);
  
  details.classList.toggle('expanded');
  icon.classList.toggle('rotated');
  
  if (details.classList.contains('expanded')) {
    btnText.textContent = 'Hide Details';
  } else {
    btnText.textContent = 'Show Details';
  }
}

// Device Info Toggle (prevent card click event)
function toggleDeviceInfo(deviceId, event) {
  event.stopPropagation(); // Prevent triggering card click
  
  const details = document.getElementById(`device-info-${deviceId}`);
  const icon = document.getElementById(`device-icon-${deviceId}`);
  const btn = document.getElementById(`device-btn-${deviceId}`);
  
  details.classList.toggle('expanded');
  icon.classList.toggle('rotated');
  
  if (details.classList.contains('expanded')) {
    btn.textContent = '✓ Device Info';
  } else {
    btn.textContent = '📋 Device Info';
  }
}

// Collapsible Section Toggle
function toggleCollapsible(sectionId) {
  const content = document.getElementById(`content-${sectionId}`);
  const icon = document.getElementById(`icon-${sectionId}`);
  
  content.classList.toggle('expanded');
  icon.classList.toggle('expanded');
}

// Enhanced renderPatients with Device Info
function renderPatientsEnhanced() {
  const grid = document.getElementById('patient-grid');
  
  if (Object.keys(patientStates).length === 0) {
    grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 40px;">No patients detected yet...</div>';
    updateSystemStats();
    return;
  }
  
  grid.innerHTML = '';
  
  for (const [deviceId, state] of Object.entries(patientStates)) {
    const card = document.createElement('div');
    card.className = 'patient-card';
    if (state.risk_score > 0.7) card.classList.add('critical');
    
    const riskPercent = (state.risk_score || 0) * 100;
    const latest = state.latest_data || {};
    
    let vitalsHTML = '';
    if (latest.HR || latest.SpO2) {
      vitalsHTML = `
        <div class="patient-vitals">
          <div class="vital-item">
            <span class="vital-icon">💓</span>
            <span class="vital-value">${latest.HR || '--'}</span>
            <span class="vital-label">bpm</span>
          </div>
          <div class="vital-item">
            <span class="vital-icon">🫁</span>
            <span class="vital-value">${latest.SpO2 || '--'}</span>
            <span class="vital-label">%</span>
          </div>
          <div class="vital-item">
            <span class="vital-icon">👤</span>
            <span class="vital-value" style="font-size: 9px;">${(latest.Posture || 'Unknown').substring(0, 8)}</span>
          </div>
          <div class="vital-item">
            <span class="vital-icon">🚶</span>
            <span class="vital-value">${latest.Steps || '--'}</span>
            <span class="vital-label">steps</span>
          </div>
        </div>
        <div class="patient-location">
          📍 ${latest.Area || 'Unknown Location'}
        </div>
      `;
    }
    
    const alertBadge = state.recent_alerts > 0 
      ? `<div class="patient-alert-badge">${state.recent_alerts} Alert${state.recent_alerts > 1 ? 's' : ''}</div>` 
      : '';
    
    const lastUpdate = state.last_update ? new Date(state.last_update).toLocaleTimeString() : 'Never';
    
    card.innerHTML = `
      <div class="patient-header" style="cursor: pointer;" onclick="showPatientDetail('${deviceId}')">
        <div class="patient-id">${deviceId}</div>
        ${alertBadge}
      </div>
      ${vitalsHTML}
      <div class="risk-meter">
        <div class="risk-fill" style="width: ${riskPercent}%"></div>
      </div>
      <div class="patient-stats">
        <span>Risk: ${(state.risk_score || 0).toFixed(2)}</span>
        <span>Data: ${state.data_points || 0}</span>
      </div>
      
      <button class="device-info-toggle" onclick="toggleDeviceInfo('${deviceId}', event)">
        <span id="device-btn-${deviceId}">📋 Device Info</span>
        <span class="expand-icon" id="device-icon-${deviceId}">▼</span>
      </button>
      
      <div class="device-info-details" id="device-info-${deviceId}">
        <div class="device-info-content">
          <div class="info-row">
            <span class="info-label">Device ID:</span>
            <span class="info-value">${deviceId}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Last Update:</span>
            <span class="info-value">${lastUpdate}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Data Points:</span>
            <span class="info-value">${state.data_points || 0}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Risk Level:</span>
            <span class="info-value" style="color: ${riskPercent > 70 ? 'var(--danger)' : riskPercent > 40 ? 'var(--warning)' : 'var(--success)'}">
              ${riskPercent > 70 ? 'HIGH' : riskPercent > 40 ? 'MEDIUM' : 'LOW'}
            </span>
          </div>
          <div class="info-row">
            <span class="info-label">Active Alerts:</span>
            <span class="info-value">${state.recent_alerts || 0}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Patterns Found:</span>
            <span class="info-value">${state.patterns?.length || 0}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Connection:</span>
            <span class="info-value" style="color: var(--success);">● Online</span>
          </div>
        </div>
      </div>
    `;
    
    grid.appendChild(card);
  }
  
  updateSystemStats();
}

// Update Agent Activity Timeline
function updateActivityTimeline(activity) {
  const timeline = document.getElementById('activity-timeline');
  
  // Remove placeholder if exists
  if (timeline.querySelector('[style*="Waiting"]')) {
    timeline.innerHTML = '';
  }
  
  // Create workflow step
  const step = document.createElement('div');
  step.className = 'workflow-step';
  
  // Add status class
  if (activity.status === 'success') {
    step.classList.add('completed');
  } else if (activity.status === 'running') {
    step.classList.add('active');
  }
  
  const time = new Date(activity.timestamp).toLocaleTimeString();
  
  step.innerHTML = `
    <div class="workflow-title">${activity.agent}</div>
    <div class="workflow-desc">${activity.action}</div>
    <div class="workflow-time">${time} | Device: ${activity.device_id || 'All'}</div>
  `;
  
  // Add to top of timeline
  timeline.insertBefore(step, timeline.firstChild);
  
  // Keep only last 10 activities
  while (timeline.children.length > 10) {
    timeline.removeChild(timeline.lastChild);
  }
}

// Update Flow Diagram based on activity
function updateFlowDiagram(activity) {
  // Reset all nodes
  const nodes = document.querySelectorAll('.flow-node');
  nodes.forEach(node => node.classList.remove('active'));
  
  // Activate relevant nodes
  const agentMap = {
    'Monitor Agent': 'flow-monitor',
    'Analyzer Agent': 'flow-analyzer',
    'Predictor Agent': 'flow-predictor',
    'Alert Agent': 'flow-alert',
    'Coordinator Agent': 'flow-coordinator'
  };
  
  const nodeId = agentMap[activity.agent];
  if (nodeId) {
    const node = document.getElementById(nodeId);
    if (node) {
      node.classList.add('active');
      
      // Remove after 2 seconds
      setTimeout(() => {
        node.classList.remove('active');
      }, 2000);
    }
  }
  
  // Always show data flow
  if (activity.action.includes('data') || activity.action.includes('sensor')) {
    document.getElementById('flow-mongodb')?.classList.add('active');
    document.getElementById('flow-listener')?.classList.add('active');
    document.getElementById('flow-state')?.classList.add('active');
    
    setTimeout(() => {
      document.getElementById('flow-mongodb')?.classList.remove('active');
      document.getElementById('flow-listener')?.classList.remove('active');
      document.getElementById('flow-state')?.classList.remove('active');
    }, 1500);
  }
}

// Update System Statistics
function updateSystemStats() {
  const totalPatients = Object.keys(patientStates).length;
  const activePatients = Object.values(patientStates).filter(p => 
    p.last_update && new Date(p.last_update) > new Date(Date.now() - 60000)
  ).length;
  
  const totalAlerts = activeAlerts.length;
  const criticalAlerts = activeAlerts.filter(a => a.severity === 'CRITICAL').length;
  
  const avgRisk = totalPatients > 0
    ? Object.values(patientStates).reduce((sum, p) => sum + (p.risk_score || 0), 0) / totalPatients
    : 0;
  
  document.getElementById('stat-total-patients').textContent = totalPatients;
  document.getElementById('stat-active-patients').textContent = activePatients;
  document.getElementById('stat-total-alerts').textContent = totalAlerts;
  document.getElementById('stat-critical-alerts').textContent = criticalAlerts;
  document.getElementById('stat-avg-risk').textContent = avgRisk.toFixed(2);
  
  // Update critical count in agent details
  document.getElementById('critical-count').textContent = criticalAlerts;
}

// Update uptime counter
let systemStartTime = Date.now();

function updateUptime() {
  const uptime = Date.now() - systemStartTime;
  const hours = Math.floor(uptime / 3600000);
  const minutes = Math.floor((uptime % 3600000) / 60000);
  const seconds = Math.floor((uptime % 60000) / 1000);
  
  const uptimeStr = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  
  const uptimeEl = document.getElementById('stat-uptime');
  if (uptimeEl) {
    uptimeEl.textContent = uptimeStr;
  }
}

// Update uptime every second
setInterval(updateUptime, 1000);

// Update agent details with last activity
function updateAgentLastActivity(agentName, timestamp) {
  const agentMap = {
    'Monitor Agent': 'monitor',
    'Analyzer Agent': 'analyzer',
    'Alert Agent': 'alert',
    'Predictor Agent': 'predictor',
    'Coordinator Agent': 'coordinator'
  };
  
  const agentKey = agentMap[agentName];
  if (agentKey) {
    const el = document.getElementById(`last-activity-${agentKey}`);
    if (el) {
      const time = new Date(timestamp).toLocaleTimeString();
      el.textContent = time;
    }
  }
}

// Initialize - replace default renderPatients
if (typeof renderPatients === 'function') {
  const originalRenderPatients = renderPatients;
  renderPatients = function() {
    renderPatientsEnhanced();
  };
}

console.log('✅ Enhanced features loaded');
