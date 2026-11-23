const DATA_URL = '/static/data/event.json';
let eventData = null;
let peopleData = [];

const safe = (value) => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));

async function loadSiteData() {
  const [eventResponse, peopleResponse] = await Promise.all([fetch(DATA_URL), fetch('/static/data/people.json')]);
  if (!eventResponse.ok || !peopleResponse.ok) throw new Error('Could not load the event information.');
  eventData = await eventResponse.json();
  peopleData = await peopleResponse.json();
  renderPeople('All');
  renderSchedule();
  renderWorkshops();
  renderVenues();
  renderPanel();
  renderConcept();
}

function personCard(person) {
  const initials = person.name.split(/\s+/).filter(Boolean).slice(0,2).map(x=>x[0]).join('').toUpperCase();
  const image = person.photo
    ? `<img class="person-photo" src="/static/images/people/${encodeURIComponent(person.photo)}" alt="Portrait of ${safe(person.name)}" loading="lazy">`
    : `<div class="person-placeholder" role="img" aria-label="No portrait supplied for ${safe(person.name)}">${safe(initials)}</div>`;
  return `<article class="person-card">${image}<h3>${safe(person.name)}</h3><p class="person-role">${safe(person.role)}</p>${person.phone ? `<a class="phone" href="tel:${safe(person.phone.replace(/\s/g,''))}">${safe(person.phone)}</a>` : ''}</article>`;
}

function renderPeople(group) {
  const filtered = group === 'All' ? peopleData.filter(person => person.group !== 'Researchers') : peopleData.filter(person => person.group === group);
  document.getElementById('peopleGrid').innerHTML = filtered.length
    ? filtered.map(personCard).join('')
    : '<p class="muted">Profiles for this group will be added soon.</p>';
  const researchers = peopleData.filter(person => person.group === 'Researchers');
  document.getElementById('researchGrid').innerHTML = researchers.map(personCard).join('');
}

function renderSchedule() {
  document.getElementById('scheduleList').innerHTML = eventData.schedule.map((item,index) => `
    <article class="schedule-item">
      <div class="schedule-time">${safe(item.time)}</div>
      <div><h3>${safe(item.title)}</h3><p>${safe(item.description)}${item.people ? `<span class="schedule-people">${safe(item.people)}</span>` : ''}</p></div>
      <div class="schedule-venue">${safe(item.venue)}</div>
    </article>`).join('');
}

function renderWorkshops() {
  document.getElementById('workshopGrid').innerHTML = eventData.workshops.map((workshop,index) => `
    <article class="workshop-card"><span class="num">WORKSHOP 0${index+1}</span><div><h4>${safe(workshop.title)}</h4><p>${safe(workshop.description)}</p></div><small>${safe(workshop.time)}<br>${safe(workshop.venue)}<br>Resource person: ${safe(workshop.resource)}</small></article>`).join('');
}

function renderVenues() {
  document.getElementById('venueGrid').innerHTML = eventData.venue_notes.map(venue => `
    <article class="venue-card"><h3>${safe(venue.place)}</h3><p>${safe(venue.detail)}</p></article>`).join('');
}

function renderPanel() {
  document.getElementById('panelSpeakers').innerHTML = eventData.panel.speakers.map(speaker => `<li>${safe(speaker)}</li>`).join('');
}

function renderConcept() {
  const note = eventData.concept_note;
  document.getElementById('conceptCopy').innerHTML = note.paragraphs.map(paragraph => `<p>${safe(paragraph)}</p>`).join('') + `<h3>Objectives</h3><ul>${note.objectives.map(item => `<li>${safe(item)}</li>`).join('')}</ul>`;
}

document.querySelectorAll('.people-tabs button').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('.people-tabs button').forEach(item => item.classList.remove('active'));
  button.classList.add('active');
  renderPeople(button.dataset.group);
}));

const menuToggle = document.getElementById('menuToggle');
const nav = document.getElementById('nav');
menuToggle.addEventListener('click', () => {
  const isOpen = nav.classList.toggle('open');
  menuToggle.setAttribute('aria-expanded', String(isOpen));
});
nav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
  nav.classList.remove('open');
  menuToggle.setAttribute('aria-expanded','false');
}));

// Event assistant: uses the Flask API. Without an API key, the server returns a verified-data response.
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const chatMessages = document.getElementById('chatMessages');
function addBubble(text, kind) {
  const bubble = document.createElement('div');
  bubble.className = `bubble ${kind}`;
  bubble.textContent = text;
  chatMessages.appendChild(bubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return bubble;
}
async function askAssistant(question) {
  addBubble(question, 'user');
  const pending = addBubble('Looking that up…', 'bot');
  try {
    const response = await fetch('/api/ask', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({question})});
    const result = await response.json();
    pending.textContent = result.answer || 'I could not find that in the event information.';
  } catch (error) {
    pending.textContent = 'The event assistant is temporarily unavailable. Please check the programme and venue sections.';
  }
  chatMessages.scrollTop = chatMessages.scrollHeight;
}
chatForm.addEventListener('submit', event => {
  event.preventDefault();
  const question = chatInput.value.trim();
  if (!question) return;
  chatInput.value = '';
  askAssistant(question);
});
document.querySelectorAll('.suggestions button').forEach(button => button.addEventListener('click', () => askAssistant(button.textContent)));

loadSiteData().catch(error => {
  console.error(error);
  document.getElementById('scheduleList').textContent = 'Event information could not be loaded. Please refresh the page.';
});
