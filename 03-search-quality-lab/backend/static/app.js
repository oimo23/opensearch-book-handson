const form = document.querySelector('#search-form')
const queryInput = document.querySelector('#query')
const submitButton = document.querySelector('#submit')
const errorBox = document.querySelector('#form-error')
const emptyState = document.querySelector('#empty-state')
const resultsBox = document.querySelector('#results')
const requestDetails = document.querySelector('#request-details')

function selectedMode() {
  return document.querySelector('input[name="mode"]:checked').value
}

function chooseMode(mode) {
  const input = document.querySelector(`input[name="mode"][value="${mode}"]`)
  if (input) input.checked = true
}

function selectedDocumentType() {
  return document.querySelector('input[name="document-type"]:checked').value
}

function chooseDocumentType(value) {
  const input = document.querySelector(`input[name="document-type"][value="${value}"]`)
  if (input) input.checked = true
}

async function loadMetadata() {
  try {
    const healthResponse = await fetch('/api/health')
    if (!healthResponse.ok) throw new Error('APIの起動を確認できませんでした。')
    const health = await healthResponse.json()
    document.querySelector('#status-dot').classList.add('ready')
    document.querySelector('#status-text').textContent = 'READY'
    document.querySelector('#index-name').textContent = health.index_name
    document.querySelector('#document-count').textContent = health.document_count
    document.querySelector('#embedding-model').textContent = health.embedding_model
  } catch (error) {
    document.querySelector('#status-text').textContent = 'NOT READY'
    showError(error.message)
  }
}

function showError(message) {
  errorBox.hidden = false
  errorBox.textContent = message
}

function clearError() {
  errorBox.hidden = true
  errorBox.textContent = ''
}

function renderResults(data) {
  emptyState.hidden = true
  resultsBox.hidden = false
  requestDetails.hidden = false
  document.querySelector('#result-title').textContent = `${data.mode} / 上位${data.hits.length}件`
  document.querySelector('#request-json').textContent = JSON.stringify(data.request_body, null, 2)

  resultsBox.replaceChildren()
  data.hits.forEach((hit, index) => {
    const article = document.createElement('article')
    article.className = 'result-card'
    article.style.animationDelay = `${index * 55}ms`
    const rerank = hit.rerank_score === null ? '' : `<span>RERANK <b>${hit.rerank_score.toFixed(4)}</b></span>`
    const context = hit.context_chunks.length === 0
      ? ''
      : `<div class="context-block"><strong>RESTORED CONTEXT</strong>${hit.context_chunks.map((chunk) => `<p><b>${chunk.chunk_order}</b> ${escapeHtml(chunk.body)}</p>`).join('')}</div>`
    const attributes = [
      hit.document_type,
      hit.product_category,
      hit.device_age_months === null ? null : `使用${hit.device_age_months}か月`,
      hit.support_outcome,
    ].filter(Boolean).map((value) => `<span>${escapeHtml(String(value))}</span>`).join('')
    article.innerHTML = `
      <div class="rank">${String(hit.rank).padStart(2, '0')}</div>
      <div>
        <h3>${escapeHtml(hit.title)}</h3>
        <div class="tags"><span>${escapeHtml(hit.id)}</span><span>${escapeHtml(hit.category)}</span>${attributes}</div>
        <p>${escapeHtml(hit.body)}</p>${context}
        <div class="scores"><span>SEARCH SCORE <b>${hit.score.toFixed(4)}</b></span>${rerank}</div>
      </div>`
    resultsBox.append(article)
  })
}

function escapeHtml(value) {
  const div = document.createElement('div')
  div.textContent = value
  return div.innerHTML
}

async function runSearch() {
  const mode = selectedMode()
  const body = {
    query: queryInput.value.trim(),
    mode,
    filters: {
      document_type: selectedDocumentType() || null,
    },
  }
  if (!body.query) return showError('質問を入力してください。')

  clearError()
  submitButton.disabled = true
  submitButton.firstChild.textContent = mode === 'hybrid_rerank' ? 'rerankモデルを実行中 ' : '検索中 '
  try {
    const response = await fetch('/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    const payload = await response.json()
    if (!response.ok) throw new Error(payload.detail || `検索に失敗しました: ${response.status}`)
    renderResults(payload)
  } catch (error) {
    showError(error.message)
  } finally {
    submitButton.disabled = false
    submitButton.firstChild.textContent = '検索して順位を比較する '
  }
}

form.addEventListener('submit', (event) => {
  event.preventDefault()
  void runSearch()
})

document.querySelectorAll('.scenario-board button').forEach((button) => {
  button.addEventListener('click', () => {
    queryInput.value = button.dataset.query
    chooseMode(button.dataset.mode)
    chooseDocumentType(button.dataset.documentType || '')
    void runSearch()
  })
})

void loadMetadata()
