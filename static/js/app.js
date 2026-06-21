/* ── FabricTrack App JS ──────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', function () {

  // ── Live Clock ────────────────────────────────────────────────────
  const clockEl = document.getElementById('currentTime');
  if (clockEl) {
    function updateClock() {
      const now = new Date();
      clockEl.textContent = now.toLocaleTimeString('en-IN', {
        hour: '2-digit', minute: '2-digit', second: '2-digit'
      });
    }
    updateClock();
    setInterval(updateClock, 1000);
  }

  // ── Sidebar Toggle (mobile) ───────────────────────────────────────
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    });
  }

  // ── Auto-dismiss alerts ───────────────────────────────────────────
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 500);
    }, 5000);
  });

  // ── Password toggle ───────────────────────────────────────────────
  const togglePwd = document.getElementById('togglePassword');
  const pwdInput  = document.getElementById('id_password');
  if (togglePwd && pwdInput) {
    togglePwd.addEventListener('click', () => {
      const isText = pwdInput.type === 'text';
      pwdInput.type = isText ? 'password' : 'text';
      togglePwd.textContent = isText ? '👁️' : '🙈';
    });
  }

  // ── Login form submit animation ───────────────────────────────────
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', function () {
      const btn = document.getElementById('btnLogin');
      if (btn) {
        btn.innerHTML = '<span>Signing in…</span>';
        btn.disabled = true;
      }
    });
  }

  // ── Auto-Calculate Average per Pcs ───────────────────────────────
  const totalPcsEl    = document.getElementById('id_total_pcs');
  const totalWeightEl = document.getElementById('id_total_weight');
  const avgPerPcsEl   = document.getElementById('id_avg_per_pcs');
  const autoCalcBadge = document.getElementById('autoCalcBadge');

  function calcAverage() {
    if (!totalPcsEl || !totalWeightEl || !avgPerPcsEl) return;
    const pcs    = parseFloat(totalPcsEl.value) || 0;
    const weight = parseFloat(totalWeightEl.value) || 0;
    if (pcs > 0 && weight > 0) {
      const avg = (weight / pcs).toFixed(3);
      avgPerPcsEl.value = avg;
      if (autoCalcBadge) autoCalcBadge.style.display = 'inline-flex';
    } else {
      avgPerPcsEl.value = '';
    }
  }

  // ── Auto-Calculate Total Pcs from Sizes ──────────────────────────
  const sizeInputs = document.querySelectorAll('.size-input');
  
  function calcTotalSizes() {
    if (!totalPcsEl || sizeInputs.length === 0) return;
    let total = 0;
    sizeInputs.forEach(input => {
      const val = parseInt(input.value, 10);
      if (!isNaN(val)) total += val;
    });
    totalPcsEl.value = total;
    calcAverage(); // Trigger average update
  }

  sizeInputs.forEach(input => {
    input.addEventListener('input', calcTotalSizes);
  });

  if (totalPcsEl)    totalPcsEl.addEventListener('input', calcAverage);
  if (totalWeightEl) totalWeightEl.addEventListener('input', calcAverage);

  // ── Auto-Calculate Total Rate (P4) ───────────────────────────────
  const darjiRateEl    = document.getElementById('id_darji_rate');
  const foldingRateEl  = document.getElementById('id_folding_rate');
  const overlockRateEl = document.getElementById('id_overlock_rate');
  const totalRateEl    = document.getElementById('id_total_rate');

  function calcTotalRate() {
    if (!totalRateEl) return;
    const darji = parseFloat(darjiRateEl?.value) || 0;
    const folding = parseFloat(foldingRateEl?.value) || 0;
    const overlock = parseFloat(overlockRateEl?.value) || 0;
    
    if (darji > 0 || folding > 0 || overlock > 0) {
      totalRateEl.value = (darji + folding + overlock).toFixed(2);
    }
  }

  if (darjiRateEl)    darjiRateEl.addEventListener('input', calcTotalRate);
  if (foldingRateEl)  foldingRateEl.addEventListener('input', calcTotalRate);
  if (overlockRateEl) overlockRateEl.addEventListener('input', calcTotalRate);

  // ── Select2 Initialization ─────────────────────────────────────────
  if (window.jQuery && $.fn.select2) {
    if (document.getElementById('id_master_entry')) {
      $('#id_master_entry').select2({ width: '100%', placeholder: 'Select Master Entry' });
    }
    if (document.getElementById('id_cutting_report')) {
      $('#id_cutting_report').select2({ width: '100%', placeholder: 'Select Cutting Report' });
    }
  }

  // ── Admin: Auto-fill Job Card No. from Master Entry dropdown ─────
  const masterEntrySelect = document.getElementById('id_master_entry');
  const jobCardNoEl       = document.getElementById('id_job_card_no');

  if (masterEntrySelect && jobCardNoEl && window.MASTER_ENTRIES) {
    const handleMasterChange = function () {
      const selectedId = this.value;
      if (selectedId && window.MASTER_ENTRIES[selectedId]) {
        jobCardNoEl.value = window.MASTER_ENTRIES[selectedId];
        // Visual flash to show it was auto-filled
        jobCardNoEl.style.transition = 'border-color 0.3s';
        jobCardNoEl.style.borderColor = '#f59e0b';
        setTimeout(() => { jobCardNoEl.style.borderColor = ''; }, 1500);
      }
    };
    
    if (window.jQuery) {
      $(masterEntrySelect).on('change', handleMasterChange);
    } else {
      masterEntrySelect.addEventListener('change', handleMasterChange);
    }
  }

  // ── Auto-fill Job Card No. or Lot No. from Cutting Report dropdown ─────
  const cuttingReportSelect = document.getElementById('id_cutting_report');
  // Form might have id_job_card_no (P2-P5) or id_lot_no (P6)
  const targetFieldEl = document.getElementById('id_job_card_no') || document.getElementById('id_lot_no');
  const itemNameEl = document.getElementById('id_item_name');
  
  if (cuttingReportSelect && targetFieldEl && window.CUTTING_REPORTS) {
    const handleCuttingChange = function () {
      const selectedId = this.value;
      if (selectedId && window.CUTTING_REPORTS[selectedId]) {
        const data = window.CUTTING_REPORTS[selectedId];
        
        // Data is now usually an object {job_card_no: '...', item_name: '...'} or {date, lot_no}
        if (typeof data === 'object') {
          targetFieldEl.value = data.lot_no || data.job_card_no || '';
          
          const dateEl = document.getElementById('id_date');
          if (dateEl && data.date) {
            dateEl.value = data.date || '';
            dateEl.style.transition = 'border-color 0.3s';
            dateEl.style.borderColor = '#f59e0b';
            setTimeout(() => { dateEl.style.borderColor = ''; }, 1500);
          }
          
          if (itemNameEl && data.item_name) {
            itemNameEl.value = data.item_name || '';
            itemNameEl.style.transition = 'border-color 0.3s';
            itemNameEl.style.borderColor = '#f59e0b';
            setTimeout(() => { itemNameEl.style.borderColor = ''; }, 1500);
          }
          
          const totalPcsEl = document.getElementById('id_total_pcs');
          if (totalPcsEl && data.total_pcs !== undefined) {
            // Only auto-fill if it's currently readonly AND there's no size grid (i.e. P4, P5, P6)
            // This prevents auto-filling in P2/P3 where total_pcs is driven by size inputs.
            if (totalPcsEl.hasAttribute('readonly') && !document.querySelector('.size-grid')) {
              totalPcsEl.value = data.total_pcs || '';
              totalPcsEl.style.transition = 'border-color 0.3s';
              totalPcsEl.style.borderColor = '#f59e0b';
              setTimeout(() => { totalPcsEl.style.borderColor = ''; }, 1500);
            }
          }
          
        } else {
          targetFieldEl.value = data;
        }
        
        // Visual flash to show it was auto-filled
        targetFieldEl.style.transition = 'border-color 0.3s';
        targetFieldEl.style.borderColor = '#f59e0b';
        setTimeout(() => { targetFieldEl.style.borderColor = ''; }, 1500);
      }
    };

    if (window.jQuery) {
      $(cuttingReportSelect).on('change', handleCuttingChange);
    } else {
      cuttingReportSelect.addEventListener('change', handleCuttingChange);
    }
  }

  // ── Multi-Photo Upload with Preview ──────────────────────────────
  const photoInput    = document.getElementById('id_photos');
  const previewGrid   = document.getElementById('photoPreviewGrid');
  const countDisplay  = document.getElementById('photoCountDisplay');
  const uploadZone    = document.getElementById('fileUploadZone');
  const MAX_PHOTOS    = 5;

  let selectedFiles = [];

  if (photoInput && previewGrid) {

    photoInput.addEventListener('change', function (e) {
      const files = Array.from(e.target.files);
      addFiles(files);
    });

    // Drag and drop
    if (uploadZone) {
      ['dragenter', 'dragover'].forEach(evt =>
        uploadZone.addEventListener(evt, (e) => {
          e.preventDefault();
          uploadZone.classList.add('drag-over');
        })
      );
      ['dragleave', 'drop'].forEach(evt =>
        uploadZone.addEventListener(evt, (e) => {
          uploadZone.classList.remove('drag-over');
        })
      );
      uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'));
        addFiles(files);
      });
    }

    function addFiles(newFiles) {
      const remaining = MAX_PHOTOS - selectedFiles.length;
      if (newFiles.length > remaining) {
        alert(`You can only upload ${MAX_PHOTOS} photos. Only the first ${remaining} will be used.`);
        newFiles = newFiles.slice(0, remaining);
      }
      newFiles.forEach(file => {
        selectedFiles.push(file);
        renderPreview(file, selectedFiles.length - 1);
      });
      syncFileInput();
      updateCountDisplay();
    }

    function renderPreview(file, index) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const item = document.createElement('div');
        item.className = 'preview-item';
        item.id = `preview-${index}`;
        item.innerHTML = `
          <img src="${e.target.result}" alt="Preview ${index + 1}" />
          <button type="button" class="preview-remove" onclick="removePhoto(${index})" title="Remove">✕</button>
        `;
        previewGrid.appendChild(item);
      };
      reader.readAsDataURL(file);
    }

    function syncFileInput() {
      try {
        // Try DataTransfer API (Chrome, Firefox, Edge)
        const dt = new DataTransfer();
        selectedFiles.forEach(f => dt.items.add(f));
        photoInput.files = dt.files;
      } catch (err) {
        // DataTransfer not available — native file input retains its own selection.
        // Photos submitted as-is from the last file picker selection.
        console.warn('DataTransfer not supported, using native file input.');
      }
    }

    function updateCountDisplay() {
      if (countDisplay) {
        countDisplay.textContent = selectedFiles.length > 0
          ? `${selectedFiles.length} of ${MAX_PHOTOS} photo${selectedFiles.length !== 1 ? 's' : ''} selected`
          : '';
      }
    }

    window.removePhoto = function (index) {
      selectedFiles.splice(index, 1);
      previewGrid.innerHTML = '';
      selectedFiles.forEach((file, i) => renderPreview(file, i));
      syncFileInput();
      updateCountDisplay();
    };
  }

  // ── Form submit loader ────────────────────────────────────────────
  const cuttingForm = document.getElementById('cuttingReportForm');
  if (cuttingForm) {
    cuttingForm.addEventListener('submit', function (e) {
      const sigInput = document.getElementById('id_signature');
      if (sigInput && !sigInput.value) {
        e.preventDefault();
        alert('Please provide your signature in the signature box before submitting.');
        const canvas = document.getElementById('signatureCanvas');
        if (canvas) {
          canvas.scrollIntoView({ behavior: 'smooth', block: 'center' });
          canvas.parentElement.style.transition = 'border-color 0.3s';
          canvas.parentElement.style.borderColor = '#ef4444';
          setTimeout(() => { canvas.parentElement.style.borderColor = ''; }, 2000);
        }
        return;
      }

      const btn = document.getElementById('btnSubmit');
      if (btn) {
        btn.querySelector('.btn-text').style.display = 'none';
        btn.querySelector('.btn-loader').style.display = 'inline';
        btn.disabled = true;
      }
    });
  }

  // ── Signature Pad ────────────────────────────────────────────────
  const canvas = document.getElementById('signatureCanvas');
  const signatureInput = document.getElementById('id_signature');
  const clearBtn = document.getElementById('btnClearSig');

  if (canvas && signatureInput) {
    const ctx = canvas.getContext('2d');
    let isDrawing = false;
    
    // Setup Canvas
    // Important: we need to set the internal resolution to match the display size
    // otherwise the mouse mapping will be wrong. We'll do this on first interact or load.
    function resizeCanvas() {
      const rect = canvas.parentElement.getBoundingClientRect();
      const parentWidth = rect.width || canvas.parentElement.clientWidth || 500;
      canvas.width = parentWidth > 0 ? parentWidth : 500;
      // Fixed height of 200px (matches CSS)
      canvas.height = 200;
      
      ctx.fillStyle = '#fff';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.strokeStyle = '#000';
      ctx.lineWidth = 3;
      ctx.lineJoin = 'round';
      ctx.lineCap = 'round';
      
      // Load and draw existing signature if present
      if (signatureInput.value) {
        const img = new Image();
        img.onload = function() {
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        };
        img.src = signatureInput.value;
      }
    }
    
    // Initialize size
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // Run on window load to ensure stylesheets are applied and parentWidth is resolved correctly
    if (document.readyState === 'complete') {
      resizeCanvas();
    } else {
      window.addEventListener('load', resizeCanvas);
    }

    function getCoordinates(e) {
      const rect = canvas.getBoundingClientRect();
      const clientX = e.clientX || (e.touches && e.touches[0].clientX);
      const clientY = e.clientY || (e.touches && e.touches[0].clientY);
      return {
        x: clientX - rect.left,
        y: clientY - rect.top
      };
    }

    function startDrawing(e) {
      isDrawing = true;
      const { x, y } = getCoordinates(e);
      ctx.beginPath();
      ctx.moveTo(x, y);
      canvas.parentElement.classList.add('focused');
      // e.preventDefault() here might break clicking inside the form, only do it on touchmove
    }

    function draw(e) {
      if (!isDrawing) return;
      if (e.type === 'touchmove') e.preventDefault(); // Prevent scrolling on touch
      const { x, y } = getCoordinates(e);
      ctx.lineTo(x, y);
      ctx.stroke();
    }

    function stopDrawing() {
      if (isDrawing) {
        ctx.closePath();
        isDrawing = false;
        canvas.parentElement.classList.remove('focused');
        signatureInput.value = canvas.toDataURL('image/png');
      }
    }

    // Mouse events
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseout', stopDrawing);

    // Touch events
    canvas.addEventListener('touchstart', startDrawing, { passive: false });
    canvas.addEventListener('touchmove', draw, { passive: false });
    canvas.addEventListener('touchend', stopDrawing);

    // Clear Signature
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        ctx.fillStyle = '#fff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        signatureInput.value = '';
      });
    }
  }

  // ── Logout Modal Logic ───────────────────────────────────────────
  const btnLogout = document.getElementById('btn-logout');
  const logoutModal = document.getElementById('logoutModal');
  const btnCancelLogout = document.getElementById('btnCancelLogout');

  if (btnLogout && logoutModal && btnCancelLogout) {
    btnLogout.addEventListener('click', function(e) {
      e.preventDefault();
      logoutModal.style.display = 'flex';
      // Close sidebar if on mobile
      if (sidebar) sidebar.classList.remove('open');
    });

    btnCancelLogout.addEventListener('click', function() {
      logoutModal.style.display = 'none';
    });

    // Close modal if user clicks outside the modal content
    logoutModal.addEventListener('click', function(e) {
      if (e.target === logoutModal) {
        logoutModal.style.display = 'none';
      }
    });
  }

});
