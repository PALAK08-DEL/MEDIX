/**
 * MEDIX Prototype — Connecting Care. Saving Lives.
 * Core Application Controller for all 5 Features.
 */

import { api } from './api.js';
import { generateQRCodeSvg } from './qr.js';

class MedixApp {
  constructor() {
    this.currentView = 'home';
    this.backendHealthy = false;
    this.activeToken = null;
    this.activeTier = 'public';
    this.selectedXrayFile = null;
    this.selectedReportFile = null;

    this.init();
  }

  init() {
    this.setupRouting();
    this.setupNavigation();
    this.checkBackendHealth();

    // Module Initializations
    this.initBloodFinder();
    this.initOrganDonation();
    this.initPatientQR();
    this.initXrayAnalysis();
    this.initReportSummarizer();

    // Initial route handling
    const initialHash = window.location.hash.replace('#', '') || 'home';
    this.navigateTo(initialHash);
  }

  // ===========================================================================
  // 1. Navigation & Routing
  // ===========================================================================
  setupRouting() {
    window.addEventListener('hashchange', () => {
      const route = window.location.hash.replace('#', '') || 'home';
      this.navigateTo(route);
    });
  }

  setupNavigation() {
    document.querySelectorAll('[data-route]').forEach(el => {
      el.addEventListener('click', (e) => {
        e.preventDefault();
        const target = el.getAttribute('data-route');
        window.location.hash = target;
      });
    });

    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    if (mobileMenuBtn && mobileMenu) {
      mobileMenuBtn.addEventListener('click', () => {
        mobileMenu.classList.toggle('hidden');
      });
      mobileMenu.querySelectorAll('[data-route]').forEach(link => {
        link.addEventListener('click', () => {
          mobileMenu.classList.add('hidden');
        });
      });
    }
  }

  navigateTo(viewName) {
    const validViews = ['home', 'blood', 'organ', 'qr', 'xray', 'report'];
    const targetView = validViews.includes(viewName) ? viewName : 'home';
    this.currentView = targetView;

    // Toggle view sections
    document.querySelectorAll('.view-section').forEach(section => {
      section.classList.remove('active-view');
    });

    const targetSection = document.getElementById(`view-${targetView}`);
    if (targetSection) {
      targetSection.classList.add('active-view');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Update nav links active styling
    document.querySelectorAll('.nav-link').forEach(link => {
      const route = link.getAttribute('data-route');
      if (route === targetView) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });

    // Lazy load data for views
    if (targetView === 'blood') this.loadBloodBanks();
    if (targetView === 'organ') this.loadTransplantCentres();
    if (targetView === 'xray') this.loadXrayPresetCases();
  }

  async checkBackendHealth() {
    const statusPill = document.getElementById('backend-status-pill');
    try {
      const health = await api.getHealth();
      this.backendHealthy = true;
      if (statusPill) {
        statusPill.innerHTML = `
          <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span class="text-xs font-semibold text-emerald-800">Backend Online</span>
        `;
        statusPill.className = "flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200";
      }
    } catch (err) {
      this.backendHealthy = false;
      if (statusPill) {
        statusPill.innerHTML = `
          <span class="w-2 h-2 rounded-full bg-rose-500"></span>
          <span class="text-xs font-semibold text-rose-800">Backend Offline</span>
        `;
        statusPill.className = "flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-rose-50 border border-rose-200";
      }
    }
  }

  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '⚠️';

    toast.innerHTML = `
      <span class="text-lg leading-none">${icon}</span>
      <div class="flex-1 font-medium">${message}</div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(12px) scale(0.96)';
      toast.style.transition = 'all 0.2s ease-out';
      setTimeout(() => toast.remove(), 250);
    }, 4500);
  }

  // ===========================================================================
  // 2. Feature 1: Blood Availability Finder
  // ===========================================================================
  initBloodFinder() {
    const groupFilter = document.getElementById('blood-group-filter');
    const searchInput = document.getElementById('blood-search-input');
    const cityFilter = document.getElementById('blood-city-filter');

    let debounceTimer;
    const triggerSearch = () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => this.loadBloodBanks(), 250);
    };

    if (groupFilter) groupFilter.addEventListener('change', triggerSearch);
    if (searchInput) searchInput.addEventListener('input', triggerSearch);
    if (cityFilter) cityFilter.addEventListener('change', triggerSearch);

    // Reservation Form
    const reserveForm = document.getElementById('blood-reserve-form');
    if (reserveForm) {
      reserveForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = reserveForm.querySelector('button[type="submit"]');
        const feedback = document.getElementById('blood-reserve-feedback');

        const bankId = document.getElementById('reserve-bank-id').value;
        const bloodGroup = document.getElementById('reserve-blood-group').value;
        const units = parseInt(document.getElementById('reserve-units').value, 10);

        if (!bankId || !bloodGroup) {
          this.showToast('Please select a facility and blood group.', 'error');
          return;
        }

        try {
          if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Securing Hold...';
          }
          if (feedback) feedback.classList.add('hidden');

          const resp = await api.reserveBloodHold(bankId, bloodGroup, units);

          if (feedback) {
            feedback.className = 'p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs';
            feedback.innerHTML = `
              <div class="font-bold flex items-center gap-1.5 text-emerald-800">
                <span>✅ Emergency Hold Confirmed</span>
                <span class="font-mono bg-emerald-100 text-emerald-900 px-1.5 py-0.5 rounded text-[11px]">${resp.reservation_id}</span>
              </div>
              <div class="mt-1">Reserved <strong>${resp.units_reserved} unit(s)</strong> of <strong>${resp.blood_group}</strong> at ${resp.bank_name}. Remaining units: ${resp.remaining_bank_units}.</div>
              <div class="text-[11px] text-emerald-700 mt-1">${resp.disclaimer}</div>
            `;
            feedback.classList.remove('hidden');
          }

          this.showToast(`Hold secured: ${resp.reservation_id}`, 'success');
          this.loadBloodBanks(); // Auto-refresh inventory
        } catch (err) {
          if (feedback) {
            feedback.className = 'p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-900 text-xs';
            feedback.innerHTML = `<strong>Hold Failed:</strong> ${err.message}`;
            feedback.classList.remove('hidden');
          }
          this.showToast(err.message, 'error');
        } finally {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Confirm Simulated Hold';
          }
        }
      });
    }

    // Donor Pledge Form
    const pledgeForm = document.getElementById('blood-pledge-form');
    if (pledgeForm) {
      pledgeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = pledgeForm.querySelector('button[type="submit"]');
        const feedback = document.getElementById('blood-pledge-feedback');

        const donorName = document.getElementById('pledge-donor-name').value.trim();
        const bloodGroup = document.getElementById('pledge-blood-group').value;
        const preferredSlot = document.getElementById('pledge-slot').value.trim();
        const bankId = document.getElementById('pledge-bank-id').value;

        if (!donorName || !bloodGroup || !preferredSlot) {
          this.showToast('Please complete all required fields.', 'error');
          return;
        }

        try {
          if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Registering Pledge...';
          }
          if (feedback) feedback.classList.add('hidden');

          const resp = await api.submitBloodDonorPledge({
            donor_name: donorName,
            blood_group: bloodGroup,
            preferred_slot: preferredSlot,
            bank_id: bankId || null
          });

          if (feedback) {
            feedback.className = 'p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs';
            feedback.innerHTML = `
              <div class="font-bold text-emerald-800">🎉 Voluntary Donor Pledge Confirmed!</div>
              <div class="mt-1">Pledge ID: <span class="font-mono bg-emerald-100 px-1 rounded">${resp.pledge_id}</span> | Donor: <strong>${resp.donor_name}</strong> (${resp.blood_group})</div>
              <div class="text-[11px] text-slate-600 mt-1">Scheduled: ${resp.preferred_slot} at ${resp.bank_name || 'Designated Regional Hub'}</div>
            `;
            feedback.classList.remove('hidden');
          }

          pledgeForm.reset();
          this.showToast(`Thank you, ${donorName}! Pledge registered.`, 'success');
        } catch (err) {
          if (feedback) {
            feedback.className = 'p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-900 text-xs';
            feedback.innerHTML = `<strong>Pledge Error:</strong> ${err.message}`;
            feedback.classList.remove('hidden');
          }
          this.showToast(err.message, 'error');
        } finally {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Submit Voluntary Donor Pledge';
          }
        }
      });
    }
  }

  async loadBloodBanks() {
    const listContainer = document.getElementById('blood-banks-list');
    const reserveBankSelect = document.getElementById('reserve-bank-id');
    const pledgeBankSelect = document.getElementById('pledge-bank-id');
    if (!listContainer) return;

    const groupFilter = document.getElementById('blood-group-filter')?.value || 'ALL';
    const searchInput = document.getElementById('blood-search-input')?.value || '';
    const cityFilter = document.getElementById('blood-city-filter')?.value || 'ALL';

    listContainer.innerHTML = `
      <div class="col-span-full py-12 text-center text-slate-400">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-teal-500 border-t-transparent mb-3"></div>
        <p class="text-xs font-semibold">Querying blood bank network...</p>
      </div>
    `;

    try {
      const data = await api.getBloodBanks({
        bloodGroup: groupFilter,
        search: searchInput,
        city: cityFilter
      });

      if (!data.results || data.results.length === 0) {
        listContainer.innerHTML = `
          <div class="col-span-full py-12 text-center text-slate-500 bg-white rounded-2xl border border-slate-200">
            <div class="text-3xl mb-2">🩸</div>
            <h4 class="font-bold text-slate-800 text-sm">No Blood Banks Found</h4>
            <p class="text-xs text-slate-500 mt-1">Try relaxing your search terms or blood group filter.</p>
          </div>
        `;
        return;
      }

      // Populate facility dropdowns if needed
      if (reserveBankSelect && reserveBankSelect.options.length <= 1) {
        data.results.forEach(b => {
          const opt = document.createElement('option');
          opt.value = b.id;
          opt.textContent = `${b.name} (${b.zone})`;
          reserveBankSelect.appendChild(opt);
        });
      }

      if (pledgeBankSelect && pledgeBankSelect.options.length <= 1) {
        data.results.forEach(b => {
          const opt = document.createElement('option');
          opt.value = b.id;
          opt.textContent = `${b.name} (${b.zone})`;
          pledgeBankSelect.appendChild(opt);
        });
      }

      listContainer.innerHTML = data.results.map(b => {
        const inventoryBadges = (b.inventory || []).map(inv => {
          let badgeColor = 'bg-emerald-50 text-emerald-800 border-emerald-200';
          if (inv.status === 'moderate') badgeColor = 'bg-amber-50 text-amber-800 border-amber-200';
          if (inv.status === 'critical') badgeColor = 'bg-rose-50 text-rose-800 border-rose-200';

          return `
            <div class="p-2 rounded-lg border text-center ${badgeColor}">
              <div class="font-mono font-extrabold text-xs">${inv.blood_group}</div>
              <div class="text-xs font-bold mt-0.5">${inv.units} u</div>
            </div>
          `;
        }).join('');

        return `
          <div class="medix-card p-5 flex flex-col justify-between">
            <div>
              <div class="flex items-start justify-between gap-3">
                <div>
                  <h4 class="font-bold text-slate-900 text-sm leading-tight">${b.name}</h4>
                  <div class="text-xs text-slate-500 mt-1 flex items-center gap-1.5">
                    <span>📍 ${b.zone}, ${b.city}</span>
                    <span>•</span>
                    <span class="font-semibold text-slate-700">${b.distance}</span>
                  </div>
                </div>
                <span class="badge-teal text-[11px] font-bold shrink-0">Verified</span>
              </div>

              <div class="mt-4">
                <div class="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-2">Simulated Inventory Status</div>
                <div class="grid grid-cols-4 gap-1.5">
                  ${inventoryBadges}
                </div>
              </div>
            </div>

            <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
              <span class="font-mono text-[11px]">📞 ${b.phone}</span>
              <button onclick="document.getElementById('reserve-bank-id').value = '${b.id}'; window.location.hash = 'blood'; document.getElementById('reserve-units').focus();"
                      class="text-teal-700 font-bold hover:underline text-xs">
                Select Facility →
              </button>
            </div>
          </div>
        `;
      }).join('');
    } catch (err) {
      listContainer.innerHTML = `
        <div class="col-span-full p-6 text-center text-rose-700 bg-rose-50 rounded-2xl border border-rose-200">
          <p class="font-bold text-sm">Failed to Load Blood Banks</p>
          <p class="text-xs mt-1">${err.message}</p>
        </div>
      `;
    }
  }

  // ===========================================================================
  // 3. Feature 2: Organ Donation & Transplant Centre
  // ===========================================================================
  initOrganDonation() {
    const organFilter = document.getElementById('organ-filter-select');
    if (organFilter) {
      organFilter.addEventListener('change', () => this.loadTransplantCentres());
    }

    // Tab buttons
    document.querySelectorAll('[data-organ-tab]').forEach(btn => {
      btn.addEventListener('click', () => {
        const targetTab = btn.getAttribute('data-organ-tab');
        document.querySelectorAll('[data-organ-tab]').forEach(b => {
          b.classList.remove('bg-teal-600', 'text-white');
          b.classList.add('bg-white', 'text-slate-700');
        });
        btn.classList.add('bg-teal-600', 'text-white');
        btn.classList.remove('bg-white', 'text-slate-700');

        document.querySelectorAll('.organ-tab-panel').forEach(p => p.classList.add('hidden'));
        const panel = document.getElementById(`organ-tab-${targetTab}`);
        if (panel) panel.classList.remove('hidden');

        if (targetTab === 'education') this.loadTransplantEducation();
      });
    });

    // Pledge Registration Form
    const organPledgeForm = document.getElementById('organ-pledge-form');
    if (organPledgeForm) {
      organPledgeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = organPledgeForm.querySelector('button[type="submit"]');
        const feedback = document.getElementById('organ-pledge-feedback');
        const cardDisplay = document.getElementById('organ-donor-card-preview');

        const donorName = document.getElementById('organ-donor-name').value.trim();
        const email = document.getElementById('organ-donor-email').value.trim();
        const bloodGroup = document.getElementById('organ-blood-group').value;
        const organs = document.getElementById('organ-pledge-selection').value.trim();
        const emergencyContact = document.getElementById('organ-emergency-contact').value.trim();
        const centreId = document.getElementById('organ-centre-id').value;

        try {
          if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Registering Organ Pledge...';
          }
          if (feedback) feedback.classList.add('hidden');

          const resp = await api.submitOrganPledge({
            donor_name: donorName,
            email: email,
            blood_group: bloodGroup,
            organs_pledged: organs,
            emergency_contact: emergencyContact,
            centre_id: centreId || null
          });

          if (feedback) {
            feedback.className = 'p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs';
            feedback.innerHTML = `
              <div class="font-bold text-emerald-800">🎉 Simulated Organ Donor Pledge Minted!</div>
              <div class="mt-1">Pledge ID: <span class="font-mono bg-emerald-100 px-1 rounded font-bold">${resp.pledge_id}</span> • Donor: ${resp.donor_name}</div>
              <div class="text-[11px] text-slate-600 mt-1">Pledged Organs: ${resp.organs_pledged}</div>
            `;
            feedback.classList.remove('hidden');
          }

          if (cardDisplay) {
            cardDisplay.classList.remove('hidden');
            document.getElementById('card-donor-name').textContent = resp.donor_name;
            document.getElementById('card-pledge-id').textContent = resp.pledge_id;
            document.getElementById('card-organs').textContent = resp.organs_pledged;
            document.getElementById('card-blood-group').textContent = bloodGroup;
          }

          this.showToast(`Pledge card generated for ${donorName}`, 'success');
        } catch (err) {
          if (feedback) {
            feedback.className = 'p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-900 text-xs';
            feedback.innerHTML = `<strong>Error:</strong> ${err.message}`;
            feedback.classList.remove('hidden');
          }
          this.showToast(err.message, 'error');
        } finally {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Mint Organ Pledge Card';
          }
        }
      });
    }
  }

  async loadTransplantCentres() {
    const listContainer = document.getElementById('transplant-centres-list');
    const organSelect = document.getElementById('organ-filter-select')?.value || 'ALL';
    const centreDropdown = document.getElementById('organ-centre-id');
    if (!listContainer) return;

    listContainer.innerHTML = `
      <div class="col-span-full py-12 text-center text-slate-400">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-teal-500 border-t-transparent mb-3"></div>
        <p class="text-xs font-semibold">Loading accredited transplant centres...</p>
      </div>
    `;

    try {
      const data = await api.getTransplantCentres(organSelect);

      if (!data.results || data.results.length === 0) {
        listContainer.innerHTML = `
          <div class="col-span-full py-10 text-center text-slate-500 bg-white rounded-2xl border border-slate-200">
            <p class="font-bold text-sm">No centres matching criteria.</p>
          </div>
        `;
        return;
      }

      if (centreDropdown && centreDropdown.options.length <= 1) {
        data.results.forEach(c => {
          const opt = document.createElement('option');
          opt.value = c.id;
          opt.textContent = `${c.name} (${c.zone})`;
          centreDropdown.appendChild(opt);
        });
      }

      listContainer.innerHTML = data.results.map(c => `
        <div class="medix-card p-5 flex flex-col justify-between">
          <div>
            <div class="flex items-start justify-between gap-3">
              <div>
                <h4 class="font-bold text-slate-900 text-sm">${c.name}</h4>
                <div class="text-xs text-slate-500 mt-0.5">📍 ${c.zone}, ${c.city} (${c.distance})</div>
              </div>
              <span class="badge-teal text-[10px] font-bold shrink-0">Grade A</span>
            </div>

            <div class="mt-3">
              <div class="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1.5">Organ Programs</div>
              <div class="flex flex-wrap gap-1">
                ${(c.organs_handled || []).map(o => `
                  <span class="text-[11px] font-medium bg-slate-100 text-slate-700 px-2 py-0.5 rounded">${o}</span>
                `).join('')}
              </div>
            </div>

            <div class="mt-3 text-xs text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              <div>⏳ <strong>Average Wait Time:</strong> ${c.avg_wait_time}</div>
              <div class="mt-1">📞 <strong>Coordinator Desk:</strong> ${c.coordinator_contact}</div>
            </div>
          </div>

          <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
            <span class="text-teal-700 font-bold">${c.verified_pledge_count} Verified Pledges</span>
            <button onclick="document.querySelector('[data-organ-tab=\\'pledge\\']').click(); document.getElementById('organ-centre-id').value = '${c.id}';"
                    class="btn-teal text-xs py-1 px-3">
              Pledge Here
            </button>
          </div>
        </div>
      `).join('');
    } catch (err) {
      listContainer.innerHTML = `
        <div class="col-span-full p-6 text-center text-rose-700 bg-rose-50 rounded-2xl border border-rose-200">
          <p class="font-bold text-sm">Failed to Load Centres</p>
          <p class="text-xs mt-1">${err.message}</p>
        </div>
      `;
    }
  }

  async loadTransplantEducation() {
    const container = document.getElementById('organ-education-container');
    if (!container) return;

    try {
      const data = await api.getTransplantEducation();
      container.innerHTML = `
        <div class="p-5 bg-teal-50/70 border border-teal-200 rounded-2xl">
          <h4 class="font-bold text-teal-900 text-sm mb-1">${data.title}</h4>
          <p class="text-xs text-slate-700 leading-relaxed">${data.overview}</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div class="p-4 bg-white rounded-xl border border-slate-200">
            <h5 class="font-bold text-slate-900 mb-2 flex items-center gap-1.5">
              <span>🌱</span> Living Donor Protocols
            </h5>
            <ul class="space-y-1.5 text-slate-600">
              ${data.living_donor_programs.map(p => `<li>• ${p}</li>`).join('')}
            </ul>
          </div>

          <div class="p-4 bg-white rounded-xl border border-slate-200">
            <h5 class="font-bold text-slate-900 mb-2 flex items-center gap-1.5">
              <span>⚖️</span> Deceased Donor Matching
            </h5>
            <ul class="space-y-1.5 text-slate-600">
              ${data.deceased_donor_protocols.map(p => `<li>• ${p}</li>`).join('')}
            </ul>
          </div>
        </div>

        <div class="p-4 bg-white rounded-xl border border-slate-200 text-xs">
          <h5 class="font-bold text-slate-900 mb-2">Frequently Asked Questions</h5>
          <div class="space-y-2.5">
            ${data.faq.map(item => `
              <div>
                <p class="font-bold text-slate-800">Q: ${item.q}</p>
                <p class="text-slate-600 mt-0.5">A: ${item.a}</p>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    } catch (err) {
      container.innerHTML = `<p class="text-xs text-rose-600">Failed to fetch educational guidelines: ${err.message}</p>`;
    }
  }

  // ===========================================================================
  // 4. Feature 3: Patient Medical Information with QR Code
  // ===========================================================================
  initPatientQR() {
    const regForm = document.getElementById('patient-reg-form');
    if (regForm) {
      regForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = regForm.querySelector('button[type="submit"]');
        const feedback = document.getElementById('patient-reg-feedback');

        const name = document.getElementById('patient-name').value.trim();
        const age = parseInt(document.getElementById('patient-age').value, 10);
        const gender = document.getElementById('patient-gender').value;
        const bloodGroup = document.getElementById('patient-blood-group').value;
        const allergies = document.getElementById('patient-allergies').value.split(',').map(s => s.trim()).filter(Boolean);
        const conditions = document.getElementById('patient-conditions').value.split(',').map(s => s.trim()).filter(Boolean);
        const meds = document.getElementById('patient-meds').value.split(',').map(s => s.trim()).filter(Boolean);
        const contactName = document.getElementById('patient-contact-name').value.trim();
        const contactPhone = document.getElementById('patient-contact-phone').value.trim();
        const organDonor = document.getElementById('patient-organ-donor').checked;
        const notes = document.getElementById('patient-notes').value.trim();

        try {
          if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Minting Secure QR...';
          }
          if (feedback) feedback.classList.add('hidden');

          const profile = await api.createPatientProfile({
            name,
            age,
            gender,
            blood_group: bloodGroup,
            allergies,
            chronic_conditions: conditions,
            medications: meds,
            emergency_contact_name: contactName,
            emergency_contact_phone: contactPhone,
            organ_donor: organDonor,
            emergency_notes: notes || null
          });

          if (feedback) {
            feedback.className = 'p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs';
            feedback.innerHTML = `✅ Profile created! Token: <span class="font-mono font-bold">${profile.security_token}</span>`;
            feedback.classList.remove('hidden');
          }

          this.showToast(`Patient QR generated: ${profile.name}`, 'success');
          this.activeToken = profile.security_token;
          this.renderQRDisplay(profile.security_token, profile.qr_resolve_url, profile);
        } catch (err) {
          if (feedback) {
            feedback.className = 'p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-900 text-xs';
            feedback.innerHTML = `<strong>Registration Error:</strong> ${err.message}`;
            feedback.classList.remove('hidden');
          }
          this.showToast(err.message, 'error');
        } finally {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Save Profile & Generate QR Code';
          }
        }
      });
    }

    // Token Lookup Bar
    const lookupBtn = document.getElementById('token-lookup-btn');
    const lookupInput = document.getElementById('token-lookup-input');
    if (lookupBtn && lookupInput) {
      lookupBtn.addEventListener('click', () => {
        const token = lookupInput.value.trim();
        if (token) {
          this.activeToken = token;
          this.resolveToken(token, this.activeTier);
        }
      });
    }

    // Access Tier Switcher Buttons
    document.querySelectorAll('[data-access-tier]').forEach(btn => {
      btn.addEventListener('click', () => {
        const tier = btn.getAttribute('data-access-tier');
        this.activeTier = tier;

        document.querySelectorAll('[data-access-tier]').forEach(b => {
          b.classList.remove('bg-teal-600', 'text-white');
          b.classList.add('bg-slate-100', 'text-slate-700');
        });
        btn.classList.add('bg-teal-600', 'text-white');
        btn.classList.remove('bg-slate-100', 'text-slate-700');

        if (this.activeToken) {
          this.resolveToken(this.activeToken, tier);
        }
      });
    });

    // Revoke QR Action
    const revokeBtn = document.getElementById('token-revoke-btn');
    if (revokeBtn) {
      revokeBtn.addEventListener('click', async () => {
        if (!this.activeToken) {
          this.showToast('No active token loaded to revoke.', 'error');
          return;
        }

        if (!confirm(`Are you sure you want to permanently revoke QR token ${this.activeToken}?`)) {
          return;
        }

        try {
          revokeBtn.disabled = true;
          const resp = await api.revokeQRToken(this.activeToken);
          this.showToast(`Token ${resp.token} has been revoked.`, 'info');

          // Immediately re-resolve to showcase the 410 Gone security response
          this.resolveToken(this.activeToken, this.activeTier);
        } catch (err) {
          this.showToast(err.message, 'error');
        } finally {
          revokeBtn.disabled = false;
        }
      });
    }

    // Pre-populate with first demo profile
    setTimeout(async () => {
      try {
        const profiles = await api.getPatientProfiles();
        if (profiles && profiles.length > 0) {
          const first = profiles[0];
          this.activeToken = first.security_token;
          if (lookupInput) lookupInput.value = first.security_token;
          this.renderQRDisplay(first.security_token, first.qr_resolve_url, first);
        }
      } catch (e) {}
    }, 500);
  }

  renderQRDisplay(token, resolveUrl, profileData = null) {
    const qrContainer = document.getElementById('qr-svg-holder');
    const tokenDisplay = document.getElementById('qr-active-token');
    const revokeBtn = document.getElementById('token-revoke-btn');

    if (tokenDisplay) tokenDisplay.textContent = token;
    if (revokeBtn) revokeBtn.classList.remove('hidden');

    if (qrContainer) {
      const svg = generateQRCodeSvg(resolveUrl || `http://127.0.0.1:8000/api/v1/patients/qr/${token}`);
      qrContainer.innerHTML = svg;
    }

    this.resolveToken(token, this.activeTier);
  }

  async resolveToken(token, tier = 'public') {
    const cardContainer = document.getElementById('patient-resolved-card');
    if (!cardContainer) return;

    cardContainer.innerHTML = `
      <div class="py-8 text-center text-slate-400">
        <div class="inline-block animate-spin rounded-full h-6 w-6 border-2 border-teal-500 border-t-transparent mb-2"></div>
        <p class="text-xs">Resolving token permissions (${tier} tier)...</p>
      </div>
    `;

    try {
      const data = await api.resolveQRToken(token, tier);

      let emrSection = '';
      if (data.extended_emr) {
        emrSection = `
          <div class="mt-4 pt-3 border-t border-slate-200 text-xs">
            <div class="font-bold text-teal-900 mb-1 flex items-center gap-1.5">
              <span>🩺</span> Authorized Paramedic Extended Record
            </div>
            <div class="space-y-1 text-slate-700">
              <div><strong>Chronic Conditions:</strong> ${(data.extended_emr.chronic_conditions || []).join(', ') || 'None documented'}</div>
              <div><strong>Active Medications:</strong> ${(data.extended_emr.current_medications || []).join(', ') || 'None'}</div>
              <div><strong>Clinical Notes:</strong> ${data.extended_emr.emergency_notes || 'None'}</div>
            </div>
          </div>
        `;
      } else {
        emrSection = `
          <div class="mt-4 p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-[11px] text-slate-500">
            🔒 <strong>Public Triage Mode:</strong> Extended medical history is masked. Switch to "Authorized Paramedic View" above to test emergency access.
          </div>
        `;
      }

      cardContainer.innerHTML = `
        <div class="p-4 rounded-xl border border-slate-200 bg-white">
          <div class="flex items-start justify-between">
            <div>
              <h4 class="font-bold text-slate-900 text-sm">${data.name}</h4>
              <div class="text-xs text-slate-500">Age: ${data.age} • Blood Group: <strong class="text-rose-700 font-mono text-sm">${data.blood_group}</strong></div>
            </div>
            <span class="badge-teal text-[10px] font-bold">${data.access_tier.toUpperCase()} TIER</span>
          </div>

          <div class="mt-3 grid grid-cols-2 gap-2 text-xs">
            <div class="p-2 bg-slate-50 rounded-lg">
              <span class="text-slate-500 text-[11px] block">Emergency Contact</span>
              <strong class="text-slate-800">${data.emergency_contact?.name || 'Not Listed'}</strong>
              <div class="font-mono text-[11px] text-slate-600">${data.emergency_contact?.phone || ''}</div>
            </div>
            <div class="p-2 bg-slate-50 rounded-lg">
              <span class="text-slate-500 text-[11px] block">Organ Donor Status</span>
              <span class="font-bold ${data.organ_donor_registered ? 'text-emerald-700' : 'text-slate-600'}">
                ${data.organ_donor_registered ? '✓ Registered Donor' : 'Not Registered'}
              </span>
            </div>
          </div>

          ${data.primary_allergies_warning && data.primary_allergies_warning.length > 0 ? `
            <div class="mt-2.5 p-2 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs">
              ⚠️ <strong>Severe Allergies:</strong> ${data.primary_allergies_warning.join(', ')}
            </div>
          ` : ''}

          ${emrSection}
        </div>
      `;
    } catch (err) {
      if (err.status === 410) {
        cardContainer.innerHTML = `
          <div class="p-5 rounded-xl bg-amber-50 border border-amber-300 text-amber-900 text-xs">
            <div class="font-bold text-sm flex items-center gap-1.5">
              <span>⛔</span> HTTP 410 Gone: QR Code Revoked
            </div>
            <p class="mt-1 leading-relaxed">
              This access token has been deactivated by the patient or hospital administration. Optical scans will not reveal any medical history.
            </p>
          </div>
        `;
      } else {
        cardContainer.innerHTML = `
          <div class="p-5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs">
            <div class="font-bold text-sm">Token Resolution Error</div>
            <p class="mt-1">${err.message}</p>
          </div>
        `;
      }
    }
  }

  // ===========================================================================
  // 5. Feature 4: AI Chest X-ray Pneumonia Detection
  // ===========================================================================
  initXrayAnalysis() {
    const fileInput = document.getElementById('xray-file-input');
    const dropzone = document.getElementById('xray-dropzone');
    const previewContainer = document.getElementById('xray-preview-container');
    const previewImg = document.getElementById('xray-preview-img');
    const analyzeBtn = document.getElementById('xray-analyze-btn');

    if (dropzone && fileInput) {
      dropzone.addEventListener('click', () => fileInput.click());

      dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('border-teal-500', 'bg-teal-50/30');
      });

      dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('border-teal-500', 'bg-teal-50/30');
      });

      dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('border-teal-500', 'bg-teal-50/30');
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
          this.handleXrayFileSelect(e.dataTransfer.files[0]);
        }
      });

      fileInput.addEventListener('change', () => {
        if (fileInput.files && fileInput.files.length > 0) {
          this.handleXrayFileSelect(fileInput.files[0]);
        }
      });
    }

    if (analyzeBtn) {
      analyzeBtn.addEventListener('click', async () => {
        if (!this.selectedXrayFile) {
          this.showToast('Please select a chest radiograph image first.', 'error');
          return;
        }

        const resultContainer = document.getElementById('xray-result-container');
        try {
          analyzeBtn.disabled = true;
          analyzeBtn.innerHTML = 'Evaluating Model Pipeline...';
          if (resultContainer) {
            resultContainer.classList.remove('hidden');
            resultContainer.innerHTML = `
              <div class="py-8 text-center text-slate-400">
                <div class="inline-block animate-spin rounded-full h-6 w-6 border-2 border-teal-500 border-t-transparent mb-2"></div>
                <p class="text-xs">Analyzing radiograph against backend model server...</p>
              </div>
            `;
          }

          const resp = await api.uploadXrayImage(this.selectedXrayFile);

          if (resultContainer) {
            resultContainer.innerHTML = `
              <div class="p-4 rounded-xl border border-slate-200 bg-white space-y-3 text-xs">
                <div class="flex items-center justify-between">
                  <div class="font-bold text-slate-800 flex items-center gap-1.5">
                    <span>🔬 Radiograph Validated:</span>
                    <span class="font-mono text-slate-600">${resp.filename}</span>
                  </div>
                  <span class="badge-demo text-[10px]">PROTOTYPE DISCLOSURE</span>
                </div>

                <div class="p-3 bg-amber-50 rounded-xl border border-amber-200 text-amber-900 leading-relaxed">
                  <strong class="block text-amber-950 mb-1">Status: ${resp.status}</strong>
                  ${resp.message}
                </div>

                <div class="p-2.5 bg-slate-50 rounded-lg text-slate-500 text-[11px]">
                  <strong>Clinical Ethics Notice:</strong> MEDIX does not synthesize fake confidence percentages when weights are unconfigured. Review the curated educational presets below for annotated triage patterns.
                </div>
              </div>
            `;
          }

          this.showToast('Radiograph validated by backend.', 'info');
        } catch (err) {
          if (resultContainer) {
            resultContainer.innerHTML = `
              <div class="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs">
                <strong>Upload Error:</strong> ${err.message}
              </div>
            `;
          }
          this.showToast(err.message, 'error');
        } finally {
          analyzeBtn.disabled = false;
          analyzeBtn.innerHTML = 'Run Pneumonia Screening';
        }
      });
    }

    // Check status
    api.getXrayStatus().then(status => {
      const banner = document.getElementById('xray-status-banner');
      if (banner) {
        banner.innerHTML = `
          <div class="flex items-center justify-between text-xs">
            <span><strong>Model Architecture:</strong> ${status.model_name}</span>
            <span class="font-mono ${status.model_available ? 'text-emerald-700' : 'text-amber-700'} font-bold">
              ${status.model_available ? '● Weights Active' : '○ Standby (Preset Mode)'}
            </span>
          </div>
        `;
      }
    }).catch(() => {});
  }

  handleXrayFileSelect(file) {
    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      this.showToast('Please select a valid image (.png, .jpeg, or .webp).', 'error');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      this.showToast('File size exceeds the 10MB limit.', 'error');
      return;
    }

    this.selectedXrayFile = file;
    const previewContainer = document.getElementById('xray-preview-container');
    const previewImg = document.getElementById('xray-preview-img');
    const filenameLabel = document.getElementById('xray-filename-label');

    if (filenameLabel) filenameLabel.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    if (previewImg) {
      const reader = new FileReader();
      reader.onload = (e) => {
        previewImg.src = e.target.result;
        if (previewContainer) previewContainer.classList.remove('hidden');
      };
      reader.readAsDataURL(file);
    }
  }

  async loadXrayPresetCases() {
    const container = document.getElementById('xray-presets-container');
    if (!container) return;

    try {
      const data = await api.getXrayPresetCases();
      container.innerHTML = data.cases.map(c => `
        <div class="medix-card p-4 space-y-2.5">
          <div class="flex items-start justify-between">
            <h5 class="font-bold text-slate-900 text-xs">${c.title}</h5>
            <span class="font-mono text-[10px] text-slate-400">${c.patient_ref}</span>
          </div>

          <div class="p-2.5 bg-slate-50 rounded-lg text-xs space-y-1">
            <div><strong>Ground Truth:</strong> ${c.ground_truth}</div>
            <div><strong>Classification:</strong> <span class="text-teal-800 font-semibold">${c.classification}</span></div>
            <div><strong>Risk Tier:</strong> <span class="font-semibold">${c.risk_tier}</span></div>
          </div>

          <div class="text-[11px] text-slate-500">
            <strong>Findings:</strong>
            <ul class="list-disc pl-4 mt-0.5 space-y-0.5">
              ${c.findings.map(f => `<li>${f}</li>`).join('')}
            </ul>
          </div>
        </div>
      `).join('');
    } catch (err) {
      container.innerHTML = `<p class="text-xs text-rose-600">Failed to load preset cases: ${err.message}</p>`;
    }
  }

  // ===========================================================================
  // 6. Feature 5: Medical Report Summarizer
  // ===========================================================================
  initReportSummarizer() {
    const summarizeBtn = document.getElementById('report-summarize-btn');
    const textArea = document.getElementById('report-text-input');
    const fileInput = document.getElementById('report-file-input');

    // Sample Loader Buttons
    document.querySelectorAll('[data-report-sample]').forEach(btn => {
      btn.addEventListener('click', () => {
        const type = btn.getAttribute('data-report-sample');
        if (type === 'er' && textArea) {
          textArea.value = `PATIENT EMERGENCY ADMISSION NOTE
Date: 2026-10-18
Chief Complaint: Acute fever, worsening productive cough, and shortness of breath for 3 days.
Vitals: BP: 124/82 mmHg, HR: 86 bpm, Temp: 38.6 C, SpO2: 95% on room air.
Assessment & Diagnosis: Community-Acquired Pneumonia and Type 2 Diabetes.
Lab Results: WBC: 13.8 K/uL, Glucose: 165 mg/dL, HbA1c: 7.2%.
Prescribed Medications: Azithromycin 500mg daily, Ceftriaxone 1g IV daily, Metformin 500mg BID.
Allergies: Penicillin (severe urticaria and bronchospasm).`;
        } else if (type === 'cardiac' && textArea) {
          textArea.value = `CARDIOLOGY CONSULTATION SUMMARY
Date: 2026-09-12
Vitals: BP: 142/90 mmHg, HR: 74 bpm, SpO2: 98%.
Impression: Essential Hypertension and Coronary Artery Disease.
Medications: Lisinopril 20mg daily, Atorvastatin 40mg daily, Aspirin 81mg daily.
Allergies: NKDA (No Known Drug Allergies).
Plan: Repeat lipid panel in 6 weeks. Encourage low-sodium diet and daily exercise.`;
        }
      });
    });

    if (summarizeBtn) {
      summarizeBtn.addEventListener('click', async () => {
        const text = textArea ? textArea.value.trim() : '';
        const file = fileInput && fileInput.files && fileInput.files.length > 0 ? fileInput.files[0] : null;

        if (!text && !file) {
          this.showToast('Please paste a medical report or upload a TXT/PDF file.', 'error');
          return;
        }

        const resultPanel = document.getElementById('report-result-panel');
        try {
          summarizeBtn.disabled = true;
          summarizeBtn.innerHTML = 'Extracting Clinical Entities...';

          if (resultPanel) {
            resultPanel.classList.remove('hidden');
            resultPanel.innerHTML = `
              <div class="py-12 text-center text-slate-400">
                <div class="inline-block animate-spin rounded-full h-6 w-6 border-2 border-teal-500 border-t-transparent mb-2"></div>
                <p class="text-xs">Extracting clinical facts, vitals, and medications...</p>
              </div>
            `;
          }

          let resp;
          if (file) {
            resp = await api.uploadReportFile(file);
          } else {
            resp = await api.summarizeReportText(text);
          }

          this.renderReportResults(resp);
          this.showToast('Report analyzed successfully.', 'success');
        } catch (err) {
          if (resultPanel) {
            resultPanel.innerHTML = `
              <div class="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs">
                <strong>Summarization Error:</strong> ${err.message}
              </div>
            `;
          }
          this.showToast(err.message, 'error');
        } finally {
          summarizeBtn.disabled = false;
          summarizeBtn.innerHTML = 'Summarize Medical Report';
        }
      });
    }

    // Check status
    api.getReportStatus().then(status => {
      const banner = document.getElementById('report-status-banner');
      if (banner) {
        banner.innerHTML = `
          <div class="text-xs text-slate-600 flex items-center justify-between">
            <span><strong>Active Extractor:</strong> ${status.fallback_engine}</span>
            <span class="text-teal-700 font-semibold">🔒 Local Privacy Preserved</span>
          </div>
        `;
      }
    }).catch(() => {});
  }

  renderReportResults(resp) {
    const resultPanel = document.getElementById('report-result-panel');
    if (!resultPanel) return;

    const h = resp.clinical_highlights;

    resultPanel.innerHTML = `
      <div class="space-y-4">
        <!-- Highlights Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          <div class="p-3 bg-white rounded-xl border border-slate-200">
            <span class="text-[11px] font-bold text-teal-800 uppercase block mb-1">🩺 Vital Signs</span>
            <ul class="text-xs space-y-0.5 text-slate-700">
              ${h.vital_signs.length ? h.vital_signs.map(v => `<li>• ${v}</li>`).join('') : '<li class="text-slate-400">None detected</li>'}
            </ul>
          </div>

          <div class="p-3 bg-white rounded-xl border border-slate-200">
            <span class="text-[11px] font-bold text-teal-800 uppercase block mb-1">📋 Diagnoses</span>
            <ul class="text-xs space-y-0.5 text-slate-700">
              ${h.diagnoses.length ? h.diagnoses.map(d => `<li>• ${d}</li>`).join('') : '<li class="text-slate-400">None detected</li>'}
            </ul>
          </div>

          <div class="p-3 bg-white rounded-xl border border-slate-200">
            <span class="text-[11px] font-bold text-teal-800 uppercase block mb-1">💊 Prescribed Meds</span>
            <ul class="text-xs space-y-0.5 text-slate-700">
              ${h.medications.length ? h.medications.map(m => `<li>• ${m}</li>`).join('') : '<li class="text-slate-400">None detected</li>'}
            </ul>
          </div>

          <div class="p-3 bg-white rounded-xl border border-slate-200">
            <span class="text-[11px] font-bold text-teal-800 uppercase block mb-1">🧪 Lab Values</span>
            <ul class="text-xs space-y-0.5 text-slate-700">
              ${h.lab_values.length ? h.lab_values.map(l => `<li>• ${l}</li>`).join('') : '<li class="text-slate-400">None detected</li>'}
            </ul>
          </div>

          <div class="p-3 bg-white rounded-xl border border-slate-200">
            <span class="text-[11px] font-bold text-rose-800 uppercase block mb-1">⚠️ Warnings & Allergies</span>
            <ul class="text-xs space-y-0.5 text-slate-700">
              ${h.warnings_and_allergies.length ? h.warnings_and_allergies.map(w => `<li class="text-rose-700 font-semibold">• ${w}</li>`).join('') : '<li class="text-slate-400">None explicitly stated</li>'}
            </ul>
          </div>

          <div class="p-3 bg-white rounded-xl border border-slate-200">
            <span class="text-[11px] font-bold text-teal-800 uppercase block mb-1">📅 Dates Documented</span>
            <ul class="text-xs space-y-0.5 text-slate-700">
              ${h.dates_and_milestones.length ? h.dates_and_milestones.map(d => `<li>• ${d}</li>`).join('') : '<li class="text-slate-400">None detected</li>'}
            </ul>
          </div>
        </div>

        <!-- Structured Summary Text -->
        <div class="p-4 bg-white rounded-xl border border-slate-200">
          <div class="flex items-center justify-between mb-2">
            <h5 class="font-bold text-slate-900 text-xs">Structured Extractive Summary</h5>
            <span class="badge-teal text-[10px]">${resp.engine}</span>
          </div>
          <pre class="font-mono text-xs text-slate-700 whitespace-pre-wrap leading-relaxed">${resp.summary_text}</pre>
        </div>

        <!-- Source Excerpt -->
        <div class="p-3.5 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-600">
          <strong class="text-slate-800">Source Document Excerpt (${resp.char_count} chars):</strong>
          <p class="font-mono text-[11px] text-slate-500 mt-1 italic">"${resp.extracted_source_excerpt}"</p>
        </div>
      </div>
    `;
  }
}

// Instantiate on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  window.medixApp = new MedixApp();
});
