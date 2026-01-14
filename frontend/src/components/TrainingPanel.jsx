import { useState } from 'react'
import axios from 'axios'

function TrainingPanel() {
  const [ddl, setDdl] = useState('')
  const [question, setQuestion] = useState('')
  const [sql, setSql] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  const handleTrainDDL = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')

    try {
      const response = await axios.post('/api/train/ddl', { ddl })
      setMessage({ type: 'success', text: response.data.message })
      setDdl('')
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.error || 'Failed to add DDL'
      })
    } finally {
      setLoading(false)
    }
  }

  const handleTrainQuery = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')

    try {
      const response = await axios.post('/api/train/query', { question, sql })
      setMessage({ type: 'success', text: response.data.message })
      setQuestion('')
      setSql('')
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.error || 'Failed to add question-SQL pair'
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="training-panel">
      <div className="section">
        <h2>Train with DDL</h2>
        <p className="section-description">
          Add your database schema (CREATE TABLE statements) to help Vanna understand your data structure.
        </p>
        <form onSubmit={handleTrainDDL}>
          <textarea
            value={ddl}
            onChange={(e) => setDdl(e.target.value)}
            placeholder="CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  name TEXT,
  email TEXT
);"
            rows="8"
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Adding...' : 'Add DDL'}
          </button>
        </form>
      </div>

      <div className="section">
        <h2>Train with Question-SQL Pairs</h2>
        <p className="section-description">
          Teach Vanna by providing example questions and their corresponding SQL queries.
        </p>
        <form onSubmit={handleTrainQuery}>
          <div className="form-group">
            <label>Question:</label>
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="What are all the users?"
              required
            />
          </div>
          <div className="form-group">
            <label>SQL:</label>
            <textarea
              value={sql}
              onChange={(e) => setSql(e.target.value)}
              placeholder="SELECT * FROM users;"
              rows="4"
              required
            />
          </div>
          <button type="submit" disabled={loading}>
            {loading ? 'Adding...' : 'Add Question-SQL Pair'}
          </button>
        </form>
      </div>

      {message && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}
    </div>
  )
}

export default TrainingPanel
