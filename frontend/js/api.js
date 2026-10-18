/**
 * MEDIX Prototype — Central API Client
 * Manages REST communication with FastAPI backend at http://127.0.0.1:8000
 */

const DEFAULT_API_BASE = 'http://127.0.0.1:8000';

export class MedixApiClient {
  constructor() {
    this.apiBase = (typeof window !== 'undefined' && window.MEDIX_API_BASE) || DEFAULT_API_BASE;
  }

  setBaseUrl(url) {
    if (url && typeof url === 'string') {
      this.apiBase = url.replace(/\/+$/, '');
    }
  }

  getBaseUrl() {
    return this.apiBase;
  }

  async _request(endpoint, options = {}) {
    const url = `${this.apiBase}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
    const defaultHeaders = {
      'Accept': 'application/json'
    };

    if (!(options.body instanceof FormData)) {
      defaultHeaders['Content-Type'] = 'application/json';
    }

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...(options.headers || {})
      }
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        let msg = data.detail || `Server error (${response.status})`;
        if (Array.isArray(msg)) {
          msg = msg.map(m => m.msg || JSON.stringify(m)).join('; ');
        }
        const error = new Error(msg);
        error.status = response.status;
        error.data = data;
        throw error;
      }

      return data;
    } catch (err) {
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        const netErr = new Error(`Cannot reach MEDIX backend at ${this.apiBase}. Is the FastAPI server running on port 8000?`);
        netErr.status = 0;
        throw netErr;
      }
      throw err;
    }
  }

  // Health
  async getHealth() {
    return this._request('/health');
  }

  // 1. Blood Availability
  async getBloodBanks(params = {}) {
    const query = new URLSearchParams();
    if (params.bloodGroup && params.bloodGroup !== 'ALL') query.append('blood_group', params.bloodGroup);
    if (params.search) query.append('search', params.search);
    if (params.city && params.city !== 'ALL') query.append('city', params.city);
    const qs = query.toString();
    return this._request(`/api/v1/blood/banks${qs ? `?${qs}` : ''}`);
  }

  async getBloodBankById(bankId) {
    return this._request(`/api/v1/blood/banks/${encodeURIComponent(bankId)}`);
  }

  async reserveBloodHold(bankId, bloodGroup, units = 1) {
    return this._request('/api/v1/blood/reserve-hold', {
      method: 'POST',
      body: JSON.stringify({
        bank_id: bankId,
        blood_group: bloodGroup,
        units: parseInt(units, 10)
      })
    });
  }

  async submitBloodDonorPledge(donorData) {
    return this._request('/api/v1/blood/donor-pledge', {
      method: 'POST',
      body: JSON.stringify(donorData)
    });
  }

  // 2. Organ Donation
  async getTransplantCentres(organ = null) {
    const query = organ && organ !== 'ALL' ? `?organ=${encodeURIComponent(organ)}` : '';
    return this._request(`/api/v1/transplant/centres${query}`);
  }

  async getTransplantEducation() {
    return this._request('/api/v1/transplant/education');
  }

  async submitOrganPledge(pledgeData) {
    return this._request('/api/v1/transplant/pledge', {
      method: 'POST',
      body: JSON.stringify(pledgeData)
    });
  }

  // 3. Patient Medical QR
  async getPatientProfiles(bloodGroup = null) {
    const query = bloodGroup && bloodGroup !== 'ALL' ? `?blood_group=${encodeURIComponent(bloodGroup)}` : '';
    return this._request(`/api/v1/patients/profiles${query}`);
  }

  async createPatientProfile(patientData) {
    return this._request('/api/v1/patients/profile', {
      method: 'POST',
      body: JSON.stringify(patientData)
    });
  }

  async resolveQRToken(token, tier = 'public') {
    return this._request(`/api/v1/patients/qr/${encodeURIComponent(token)}?tier=${encodeURIComponent(tier)}`);
  }

  async revokeQRToken(token) {
    return this._request('/api/v1/patients/qr/revoke', {
      method: 'POST',
      body: JSON.stringify({ token })
    });
  }

  // 4. AI Chest X-ray
  async getXrayStatus() {
    return this._request('/api/v1/xray/status');
  }

  async getXrayPresetCases() {
    return this._request('/api/v1/xray/cases');
  }

  async getXrayCaseById(caseId) {
    return this._request(`/api/v1/xray/cases/${encodeURIComponent(caseId)}`);
  }

  async uploadXrayImage(file) {
    const formData = new FormData();
    formData.append('file', file);
    return this._request('/api/v1/xray/predict', {
      method: 'POST',
      body: formData
    });
  }

  // 5. Medical Report Summarizer
  async getReportStatus() {
    return this._request('/api/v1/reports/status');
  }

  async summarizeReportText(reportText, patientContext = 'Clinical Report') {
    return this._request('/api/v1/reports/summarize', {
      method: 'POST',
      body: JSON.stringify({
        report_text: reportText,
        patient_context: patientContext
      })
    });
  }

  async uploadReportFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    return this._request('/api/v1/reports/upload', {
      method: 'POST',
      body: formData
    });
  }
}

export const api = new MedixApiClient();
export default api;
