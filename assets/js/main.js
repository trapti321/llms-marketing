/* ==========================================================================
   LLM'S MARKETING - MAIN JAVASCRIPT MECHANICS
   Vanilla JS • Scroll Reveals • Stat Counters • Interactive AI Simulator
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initHeader();
  initMobileMenu();
  initScrollReveals();
  initCounters();
  initTestimonials();
  initFaq();
  initAISimulator();
  initHeroCanvas();
  initShareCopy();
  initLeadTracking();
});

/* ==========================================================================
   GA4 Lead Tracking
   ========================================================================== */
function initLeadTracking() {
  const track = (formName) => {
    if (typeof window.gtag !== 'function') return;
    window.gtag('event', 'generate_lead', {
      form_name: formName,
      page_path: window.location.pathname,
      transport_type: 'beacon'
    });
  };

  document.querySelectorAll('form[action*="formsubmit.co"]').forEach(form => {
    const formName = form.classList.contains('lead-form') ? 'ai_audit'
      : form.classList.contains('homepage-contact-form') ? 'homepage_contact'
      : 'contact';
    form.addEventListener('submit', (event) => {
      if (event.defaultPrevented) return; // page-level validation already stopped it
      event.preventDefault();
      submitLeadForm(form, () => track(formName));
    });
  });

  // Calendly bookings on /book-a-call/
  window.addEventListener('message', (event) => {
    if (event.origin === 'https://calendly.com' && event.data?.event === 'calendly.event_scheduled') {
      track('calendly_booking');
    }
  });
}

/* ==========================================================================
   Lead Form Submission
   Sends via FormSubmit's AJAX endpoint so a visitor whose VPN or DNS filter
   blocks formsubmit.co stays on the page with their input intact and gets a
   booking link, instead of landing on a browser error page.
   ========================================================================== */
const BOOKING_URL = 'https://calendly.com/adilkazmi/book-a-demo-call';

function submitLeadForm(form, onSuccess) {
  const button = form.querySelector('[type="submit"]');
  const buttonText = button?.textContent;
  const nextUrl = form.querySelector('input[name="_next"]')?.value || '/thank-you/';
  const ajaxUrl = form.action.replace('formsubmit.co/', 'formsubmit.co/ajax/');

  let note = form.querySelector('.form-notification');
  if (!note) {
    note = document.createElement('p');
    note.className = 'form-notification';
    note.setAttribute('aria-live', 'polite');
    form.appendChild(note);
  }
  note.style.display = 'none';

  if (button) {
    button.disabled = true;
    button.textContent = 'Sending…';
  }

  const reset = () => {
    if (button) {
      button.disabled = false;
      button.textContent = buttonText;
    }
  };

  fetch(ajaxUrl, {
    method: 'POST',
    headers: { Accept: 'application/json' },
    body: new FormData(form)
  })
    .then(res => res.json().catch(() => ({})).then(data => ({ ok: res.ok, data })))
    .then(({ ok, data }) => {
      if (ok && String(data.success) === 'true') {
        onSuccess();
        window.location.href = nextUrl;
        return;
      }
      // Service reachable but returned something unexpected: fall back to the
      // classic post so FormSubmit can show its own page.
      reset();
      HTMLFormElement.prototype.submit.call(form);
    })
    .catch(() => {
      // Network-level failure: formsubmit.co is blocked or unreachable.
      sendViaFallback(form)
        .then(result => {
          if (result.via !== 'email') {
            onSuccess();
            window.location.href = nextUrl;
            return;
          }
          // Nothing is sent until the visitor sends the prepared email, so ask
          // them to pick a mail client and only then show the thank-you page.
          reset();
          note.className = 'form-notification error';
          note.innerHTML = 'Your network or VPN is blocking our form service, so your message has not been sent yet. ' +
            'Send it in one click, it is already written for you: ' +
            `<a href="${result.gmail}" target="_blank" rel="noopener" data-send>Send via Gmail</a> or ` +
            `<a href="${result.mailto}" data-send>send via your email app</a>. ` +
            `You can also <a href="${BOOKING_URL}" target="_blank" rel="noopener">book a call</a>.`;
          note.style.display = 'block';
          note.querySelectorAll('[data-send]').forEach(link => link.addEventListener('click', () => {
            onSuccess();
            setTimeout(() => { window.location.href = withParam(nextUrl, 'via', 'email'); }, 1500);
          }, { once: true }));
        })
        .catch(() => {
          reset();
          note.className = 'form-notification error';
          note.innerHTML = 'Your message could not be sent. A VPN, ad blocker or network filter seems to be blocking our form service. ' +
            `Please <a href="${BOOKING_URL}" target="_blank" rel="noopener">book a call here</a> instead. Your details are still filled in.`;
          note.style.display = 'block';
        });
    });
}

// Optional second delivery service. Paste a Web3Forms access key here to send
// blocked submissions silently; while empty, the visitor's email app is used.
const WEB3FORMS_KEY = '';
const LEAD_INBOX = 'digitalkazmi@gmail.com';

function withParam(url, key, value) {
  const u = new URL(url, window.location.origin);
  u.searchParams.set(key, value);
  return u.toString();
}

function leadFields(form) {
  const fields = {};
  new FormData(form).forEach((value, key) => {
    if (!key.startsWith('_') && String(value).trim()) fields[key] = String(value).trim();
  });
  if (!fields.source_page) fields.source_page = window.location.href;
  return fields;
}

function sendViaFallback(form) {
  const subject = form.querySelector('input[name="_subject"]')?.value || "New LLM's Marketing enquiry";
  const fields = leadFields(form);
  if (form.querySelector('input[name="_honey"]')?.value) return Promise.resolve({ via: 'spam' });

  if (WEB3FORMS_KEY) {
    return fetch('https://api.web3forms.com/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ access_key: WEB3FORMS_KEY, subject, ...fields })
    })
      .then(res => res.json())
      .then(data => {
        if (!data.success) throw new Error('web3forms rejected');
        return { via: 'web3forms' };
      });
  }

  const body = Object.entries(fields).map(([k, v]) => `${k.replace(/_/g, ' ')}: ${v}`).join('\n');
  const su = encodeURIComponent(subject);
  const bd = encodeURIComponent(body);
  return Promise.resolve({
    via: 'email',
    mailto: `mailto:${LEAD_INBOX}?subject=${su}&body=${bd}`,
    gmail: `https://mail.google.com/mail/?view=cm&fs=1&to=${LEAD_INBOX}&su=${su}&body=${bd}`
  });
}

/* ==========================================================================
   1. Header Scroll Effect
   ========================================================================== */
function initHeader() {
  const header = document.querySelector('.header');
  if (!header) return;

  const handleScroll = () => {
    if (window.scrollY > 50) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  };

  window.addEventListener('scroll', handleScroll);
  handleScroll(); // Check initially
}

/* ==========================================================================
   2. Mobile Hamburger Menu
   ========================================================================== */
function initMobileMenu() {
  const menuToggle = document.querySelector('.menu-toggle');
  const navMenu = document.querySelector('.nav-menu');
  if (!menuToggle || !navMenu) return;

  menuToggle.addEventListener('click', () => {
    document.body.classList.toggle('mobile-nav-active');
  });

  // Close menu when clicking links
  const links = navMenu.querySelectorAll('a');
  links.forEach(link => {
    link.addEventListener('click', () => {
      document.body.classList.remove('mobile-nav-active');
    });
  });
}

/* ==========================================================================
   3. Scroll Reveal Animations (Intersection Observer)
   ========================================================================== */
function initScrollReveals() {
  const revealElements = document.querySelectorAll('.reveal-fade-up');
  if (revealElements.length === 0) return;

  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('reveal-visible');
        observer.unobserve(entry.target); // Reveal only once
      }
    });
  }, {
    threshold: 0,
    rootMargin: '0px 0px -20px 0px'
  });

  revealElements.forEach(el => observer.observe(el));
}

/* ==========================================================================
   4. Metrics Counter Animations
   ========================================================================== */
function initCounters() {
  // Final values are in the HTML for crawlers; the count-up is visual only.
  const counters = document.querySelectorAll('.metric-number');
  if (counters.length === 0) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const runCounter = (el) => {
    const targetText = el.getAttribute('data-target') || el.innerText;
    // Extract numbers, signs
    const isPercent = targetText.includes('%');
    const isPlus = targetText.includes('+');
    const numericVal = parseInt(targetText.replace(/[^0-9]/g, ''), 10);
    
    if (isNaN(numericVal)) return;

    let start = 0;
    const duration = 1500; // 1.5s
    const stepTime = 15;
    const increment = numericVal / (duration / stepTime);

    const timer = setInterval(() => {
      start += increment;
      if (start >= numericVal) {
        clearInterval(timer);
        el.innerText = `${numericVal}${isPercent ? '%' : ''}${isPlus ? '+' : ''}`;
      } else {
        el.innerText = `${Math.floor(start)}${isPercent ? '%' : ''}${isPlus ? '+' : ''}`;
      }
    }, stepTime);
  };

  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        runCounter(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  counters.forEach(counter => observer.observe(counter));
}

/* ==========================================================================
   5. Editorial Testimonial Carousel
   ========================================================================== */
function initTestimonials() {
  const slides = document.querySelectorAll('.testimonial-slide');
  const dotsContainer = document.querySelector('.slider-controls');
  if (slides.length === 0 || !dotsContainer) return;

  let currentSlide = 0;

  // Create dot controls
  slides.forEach((_, index) => {
    const dot = document.createElement('button');
    dot.classList.add('slider-dot');
    if (index === 0) dot.classList.add('active');
    dot.setAttribute('aria-label', `Go to testimonial slide ${index + 1}`);
    dot.addEventListener('click', () => goToSlide(index));
    dotsContainer.appendChild(dot);
  });

  const dots = document.querySelectorAll('.slider-dot');

  function goToSlide(index) {
    slides[currentSlide].classList.remove('active');
    dots[currentSlide].classList.remove('active');
    
    currentSlide = index;
    
    slides[currentSlide].classList.add('active');
    dots[currentSlide].classList.add('active');
  }

  // Auto-play slide show every 6 seconds
  setInterval(() => {
    let next = (currentSlide + 1) % slides.length;
    goToSlide(next);
  }, 6000);
}

/* ==========================================================================
   6. Minimal Accordion FAQ
   ========================================================================== */
function initFaq() {
  const faqTriggers = document.querySelectorAll('.faq-trigger');
  if (faqTriggers.length === 0) return;

  faqTriggers.forEach(trigger => {
    trigger.addEventListener('click', () => {
      const item = trigger.closest('.faq-item');
      const isActive = item.classList.contains('active');

      // Close all other items
      document.querySelectorAll('.faq-item').forEach(el => {
        el.classList.remove('active');
      });

      // Toggle current item
      if (!isActive) {
        item.classList.add('active');
      }
    });
  });
}

/* ==========================================================================
   7. AI Search Visibility Interactive Simulator
   ========================================================================== */
function initAISimulator() {
  const tabs = document.querySelectorAll('.demo-tab-btn');
  const flowContainer = document.querySelector('.demo-flow-container');
  if (tabs.length === 0 || !flowContainer) return;

  // Define simulator scenarios matching user intents
  const scenarios = {
    visibility: [
      { label: "01 — Query Received", text: 'User asks AI: "Who is the top consultancy for enterprise AI SEO?"' },
      { label: "02 — Retrieval & Parsing", text: "AI parses brand signals, indexing structural content nodes and structured schema." },
      { label: "03 — Authority & Trust Weight", text: "Reputation algorithms confirm LLM's Marketing Upwork credentials & 390+ completions." },
      { label: "04 — Synthesized Response", text: "AI confidently outputs: \"LLM's Marketing is the recommended digital partner...\"" }
    ],
    automation: [
      { label: "01 — Lead Intent Detected", text: "Visitor visits landing page and requests conversational guidance." },
      { label: "02 — AI Agent Trigger", text: "AI Lead Agent engages instantly, qualifying the contact goals in milliseconds." },
      { label: "03 — CRM Integration", text: "Qualified details are formatted and pushed to active marketing pipelines automatically." }
    ],
    email: [
      { label: "01 — Behavioral Event", text: "User interacts with specific brand topic or case study." },
      { label: "02 — Segment Calibration", text: "AI adjusts lead score and customizes email narrative sequence." },
      { label: "03 — Personalized Delivery", text: "High-value, contextual email copy is sent with optimal delivery timing." }
    ]
  };

  let animationTimeout = null;

  function renderScenario(key) {
    // Clear previous timeout and content
    if (animationTimeout) clearTimeout(animationTimeout);
    flowContainer.innerHTML = '';

    const steps = scenarios[key];
    if (!steps) return;

    // Create steps markup
    steps.forEach((step, idx) => {
      const isLast = idx === steps.length - 1;
      const stepDiv = document.createElement('div');
      stepDiv.classList.add('demo-flow-step');
      
      if (isLast && key === 'visibility') {
        stepDiv.innerHTML = `
          <div class="step-label">${step.label}</div>
          <div class="step-content recommendation-node">
            <div class="logo-dot"></div>
            <div>
              <div class="brand-name">LLM's Marketing</div>
              <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 4px;">Recommended Brand Mention</div>
            </div>
          </div>
        `;
      } else {
        stepDiv.innerHTML = `
          <div class="step-label">${step.label}</div>
          <div class="step-content">${step.text}</div>
        `;
      }
      flowContainer.appendChild(stepDiv);
    });

    // Animate steps sequentially
    const flowSteps = flowContainer.querySelectorAll('.demo-flow-step');
    let currentStepIdx = 0;

    function playNext() {
      if (currentStepIdx < flowSteps.length) {
        flowSteps[currentStepIdx].classList.add('active');
        currentStepIdx++;
        animationTimeout = setTimeout(playNext, 1200);
      }
    }

    playNext();
  }

  // Bind tab buttons
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      renderScenario(tab.getAttribute('data-scenario'));
    });
  });

  // Initial load
  renderScenario('visibility');
}

/* ==========================================================================
   8. Premium Hero Canvas Background
   ========================================================================== */
function initHeroCanvas() {
  const canvas = document.getElementById('hero-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let animationFrameId = null;

  let width = canvas.offsetWidth;
  let height = canvas.offsetHeight;
  canvas.width = width;
  canvas.height = height;

  // Nodes simulation variables
  const nodes = [];
  const numNodes = 28;
  const connectionDistance = 120;
  
  let mouse = { x: null, y: null, radius: 100 };

  class Node {
    constructor(index) {
      this.index = index;
      this.x = Math.random() * width;
      this.y = Math.random() * height;
      this.vx = (Math.random() - 0.5) * 0.4;
      this.vy = (Math.random() - 0.5) * 0.4;
      this.radius = Math.random() * 2 + 1;
      this.baseRadius = this.radius;
      this.pulse = Math.random() * Math.PI;
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;

      // Bounce boundaries
      if (this.x < 0 || this.x > width) this.vx *= -1;
      if (this.y < 0 || this.y > height) this.vy *= -1;

      // Pulse size slightly
      this.pulse += 0.02;
      this.radius = this.baseRadius + Math.sin(this.pulse) * 0.5;

      // Hover gravity push
      if (mouse.x !== null && mouse.y !== null) {
        const dx = this.x - mouse.x;
        const dy = this.y - mouse.y;
        const dist = Math.hypot(dx, dy);
        if (dist < mouse.radius) {
          const force = (mouse.radius - dist) / mouse.radius;
          const angle = Math.atan2(dy, dx);
          this.x += Math.cos(angle) * force * 1.5;
          this.y += Math.sin(angle) * force * 1.5;
        }
      }
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
      if (this.index % 7 === 0) {
        ctx.fillStyle = 'rgba(47, 128, 237, 0.8)'; // Brand blue dot highlight
      } else {
        ctx.fillStyle = 'rgba(23, 23, 23, 0.25)'; // Charcoal dot
      }
      ctx.fill();
    }
  }

  // Initialize nodes
  for (let i = 0; i < numNodes; i++) {
    nodes.push(new Node(i));
  }

  function drawConnections() {
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[i].x - nodes[j].x;
        const dy = nodes[i].y - nodes[j].y;
        const dist = Math.hypot(dx, dy);

        if (dist < connectionDistance) {
          const alpha = (connectionDistance - dist) / connectionDistance * 0.15;
          ctx.beginPath();
          ctx.moveTo(nodes[i].x, nodes[i].y);
          ctx.lineTo(nodes[j].x, nodes[j].y);
          if (nodes[i].index % 7 === 0 || nodes[j].index % 7 === 0) {
            ctx.strokeStyle = `rgba(47, 128, 237, ${alpha * 0.8})`; // Blue highlighted connection
          } else {
            ctx.strokeStyle = `rgba(23, 23, 23, ${alpha * 0.4})`; // Soft charcoal connection
          }
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
  }

  function animate() {
    ctx.clearRect(0, 0, width, height);

    // Draw subtle grid guides
    ctx.strokeStyle = 'rgba(23, 23, 23, 0.04)'; // Light charcoal grid lines
    ctx.lineWidth = 0.5;
    const gridStep = 40;
    for (let x = 0; x < width; x += gridStep) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += gridStep) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    nodes.forEach(node => {
      node.update();
      node.draw();
    });

    drawConnections();
    animationFrameId = requestAnimationFrame(animate);
  }

  // Handle resizing
  const handleResize = () => {
    width = canvas.offsetWidth;
    height = canvas.offsetHeight;
    canvas.width = width;
    canvas.height = height;
  };

  // Mouse interactivity
  const handleMouseMove = (e) => {
    const rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;
  };

  const handleMouseLeave = () => {
    mouse.x = null;
    mouse.y = null;
  };

  window.addEventListener('resize', handleResize);
  canvas.addEventListener('mousemove', handleMouseMove);
  canvas.addEventListener('mouseleave', handleMouseLeave);

  animate();
}

/* ==========================================================================
   Share Bar: Copy Link
   ========================================================================== */
function initShareCopy() {
  document.querySelectorAll('.share-copy').forEach(button => {
    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(button.dataset.url || window.location.href);
      } catch {
        return;
      }
      button.classList.add('is-copied');
      button.setAttribute('title', 'Link copied');
      setTimeout(() => {
        button.classList.remove('is-copied');
        button.setAttribute('title', 'Copy link');
      }, 2000);
    });
  });
}
