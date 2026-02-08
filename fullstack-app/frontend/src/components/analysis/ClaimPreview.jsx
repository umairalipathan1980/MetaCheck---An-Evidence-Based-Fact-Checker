import { useState, useEffect } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'

export function ClaimPreview({ extractedData, onVerifySelected, mode, disabled = false }) {
  const [selectedIndices, setSelectedIndices] = useState([])
  const [currentPage, setCurrentPage] = useState(0)

  const claims = extractedData?.claims || []
  const maxVerifiable = extractedData?.max_verifiable || 10
  const CLAIMS_PER_PAGE = 5

  // Calculate pagination
  const totalPages = Math.ceil(claims.length / CLAIMS_PER_PAGE)
  const startIndex = currentPage * CLAIMS_PER_PAGE
  const endIndex = Math.min(startIndex + CLAIMS_PER_PAGE, claims.length)
  const currentPageClaims = claims.slice(startIndex, endIndex)

  // Auto-select up to max_verifiable claims on initial load
  useEffect(() => {
    if (claims.length > 0 && selectedIndices.length === 0) {
      const initialSelection = claims
        .slice(0, Math.min(claims.length, maxVerifiable))
        .map((_, index) => index)
      setSelectedIndices(initialSelection)
    }
  }, [claims.length, maxVerifiable])

  // Reset to first page when claims change
  useEffect(() => {
    setCurrentPage(0)
  }, [claims.length])

  const toggleClaim = (index) => {
    setSelectedIndices((prev) => {
      if (prev.includes(index)) {
        return prev.filter((i) => i !== index)
      } else {
        if (prev.length >= maxVerifiable) {
          return prev // Don't allow selection beyond max
        }
        return [...prev, index].sort((a, b) => a - b)
      }
    })
  }

  const selectAll = () => {
    const allIndices = claims.slice(0, maxVerifiable).map((_, index) => index)
    setSelectedIndices(allIndices)
  }

  const deselectAll = () => {
    setSelectedIndices([])
  }

  const handleVerify = () => {
    if (selectedIndices.length > 0) {
      const selectedClaimTexts = selectedIndices
        .map((index) => claims[index]?.text)
        .filter(Boolean)
      onVerifySelected(selectedIndices, selectedClaimTexts)
    }
  }

  if (!extractedData || claims.length === 0) {
    return null
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Select Claims to Verify</h2>
          <p className="text-sm text-gray-600 mt-1">
            {extractedData.total_extracted} claim{extractedData.total_extracted !== 1 ? 's' : ''} extracted •{' '}
            {selectedIndices.length} selected •{' '}
            Max {maxVerifiable} in {mode} mode
            {totalPages > 1 && ` • Page ${currentPage + 1} of ${totalPages}`}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={selectAll}
            disabled={disabled || claims.length === 0}
            className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 disabled:opacity-50"
          >
            Select All
          </button>
          <button
            onClick={deselectAll}
            disabled={disabled || selectedIndices.length === 0}
            className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 disabled:opacity-50"
          >
            Deselect All
          </button>
        </div>
      </div>

      <div className="space-y-3 mb-4">
        {currentPageClaims.map((claim, pageIndex) => {
          const index = startIndex + pageIndex
          const isSelected = selectedIndices.includes(index)
          const isDisabled = !isSelected && selectedIndices.length >= maxVerifiable

          return (
            <div
              key={index}
              className={`p-4 rounded border-2 transition-all ${
                isSelected
                  ? 'border-blue-500 bg-blue-50'
                  : isDisabled
                  ? 'border-gray-200 bg-gray-50 opacity-50'
                  : 'border-gray-200 bg-white hover:border-blue-300'
              }`}
            >
              <div className="flex items-start gap-3">
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => toggleClaim(index)}
                  disabled={disabled || isDisabled}
                  className="mt-1 w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <div className="flex-1">
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-gray-800 font-medium">{claim.text}</p>
                    <span
                      className={`px-2 py-1 text-xs rounded-full whitespace-nowrap ${
                        claim.worthiness_score >= 0.8
                          ? 'bg-green-100 text-green-800'
                          : claim.worthiness_score >= 0.6
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      Worthiness: {(claim.worthiness_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Claim #{index + 1}</p>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {claims.length > maxVerifiable && (
        <div className="bg-yellow-50 border border-yellow-200 rounded p-3 mb-4">
          <p className="text-sm text-yellow-800">
            <strong>Note:</strong> Only {maxVerifiable} claims can be verified in {mode} mode.
            {extractedData.total_extracted - maxVerifiable} claim{extractedData.total_extracted - maxVerifiable !== 1 ? 's' : ''} cannot be selected.
          </p>
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 mb-4">
          <button
            onClick={() => setCurrentPage((prev) => Math.max(0, prev - 1))}
            disabled={currentPage === 0 || disabled}
            className="flex items-center gap-1 px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </button>
          <span className="text-sm text-gray-600 px-4">
            Page {currentPage + 1} of {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage((prev) => Math.min(totalPages - 1, prev + 1))}
            disabled={currentPage === totalPages - 1 || disabled}
            className="flex items-center gap-1 px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      )}

      <div className="flex items-center justify-between pt-4 border-t">
        <p className="text-sm text-gray-600">
          {selectedIndices.length === 0 ? (
            <span className="text-red-600 font-medium">Please select at least one claim to verify</span>
          ) : (
            <span>
              Ready to verify {selectedIndices.length} claim{selectedIndices.length !== 1 ? 's' : ''}
            </span>
          )}
        </p>
        <button
          onClick={handleVerify}
          disabled={disabled || selectedIndices.length === 0}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
        >
          Verify Selected Claims
        </button>
      </div>
    </div>
  )
}
