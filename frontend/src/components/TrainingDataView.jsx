import { useState, useEffect } from 'react'
import axios from 'axios'

function TrainingDataView() {
  const [trainingData, setTrainingData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchTrainingData()
  }, [])

  const fetchTrainingData = async () => {
    setLoading(true)
    setError('')

    try {
      const response = await axios.get('/api/training-data')
      setTrainingData(response.data.data)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch training data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading training data...</div>
  }

  if (error) {
    return <div className="message error">{error}</div>
  }

  if (!trainingData) {
    return null
  }

  return (
    <div className="training-data-view">
      <div className="section">
        <div className="section-header">
          <h2>Training Data</h2>
          <button onClick={fetchTrainingData} className="refresh-btn">
            Refresh
          </button>
        </div>

        {trainingData.length === 0 ? (
          <div className="message info">
            No training data yet. Start by adding DDL or question-SQL pairs in the Train Model tab.
          </div>
        ) : (
          <div className="training-items">
            {trainingData.map((item, idx) => (
              <div key={idx} className="training-item">
                <div className="item-type">
                  {item.training_data_type || 'Unknown Type'}
                </div>
                <div className="item-content">
                  {item.question && (
                    <div className="item-field">
                      <strong>Question:</strong> {item.question}
                    </div>
                  )}
                  {item.content && (
                    <div className="item-field">
                      <strong>Content:</strong>
                      <pre>{item.content}</pre>
                    </div>
                  )}
                  {item.sql && (
                    <div className="item-field">
                      <strong>SQL:</strong>
                      <pre>{item.sql}</pre>
                    </div>
                  )}
                  {item.id && (
                    <div className="item-id">ID: {item.id}</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default TrainingDataView
