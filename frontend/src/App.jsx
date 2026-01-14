import { useState } from 'react'
import TrainingPanel from './components/TrainingPanel'
import QueryPanel from './components/QueryPanel'
import TrainingDataView from './components/TrainingDataView'

function App() {
  const [activeTab, setActiveTab] = useState('query')

  return (
    <div className="app">
      <header className="app-header">
        <h1>Vanna AI - SQL Query Assistant</h1>
        <p className="subtitle">Train the AI and ask questions in natural language</p>
      </header>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'query' ? 'active' : ''}`}
          onClick={() => setActiveTab('query')}
        >
          Ask Questions
        </button>
        <button
          className={`tab ${activeTab === 'train' ? 'active' : ''}`}
          onClick={() => setActiveTab('train')}
        >
          Train Model
        </button>
        <button
          className={`tab ${activeTab === 'data' ? 'active' : ''}`}
          onClick={() => setActiveTab('data')}
        >
          View Training Data
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'query' && <QueryPanel />}
        {activeTab === 'train' && <TrainingPanel />}
        {activeTab === 'data' && <TrainingDataView />}
      </div>
    </div>
  )
}

export default App
