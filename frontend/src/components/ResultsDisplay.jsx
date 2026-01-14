function ResultsDisplay({ results, columns }) {
  if (!results || results.length === 0) {
    return <div className="no-results">No results to display</div>
  }

  return (
    <div className="results-table-container">
      <table className="results-table">
        <thead>
          <tr>
            {columns && columns.map((col, idx) => (
              <th key={idx}>{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {results.map((row, rowIdx) => (
            <tr key={rowIdx}>
              {columns && columns.map((col, colIdx) => (
                <td key={colIdx}>
                  {row[col] !== null && row[col] !== undefined
                    ? String(row[col])
                    : 'NULL'}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="results-count">
        {results.length} row{results.length !== 1 ? 's' : ''} returned
      </div>
    </div>
  )
}

export default ResultsDisplay
