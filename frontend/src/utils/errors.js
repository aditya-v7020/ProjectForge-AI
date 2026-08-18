/**
 * Safely extracts human-readable error messages from Axios / API errors or generic JS errors.
 * Prevents React rendering crashes when FastAPI returns validation error objects or arrays.
 * 
 * @param {any} err - The caught error
 * @param {string} defaultMsg - Fallback message
 * @returns {string}
 */
export function getErrorMessage(err, defaultMsg = 'An unexpected error occurred.') {
  if (!err) return defaultMsg;

  const detail = err.response?.data?.detail;

  if (typeof detail === 'string' && detail.trim().length > 0) {
    return detail;
  }

  if (Array.isArray(detail)) {
    const messages = detail.map((d) => {
      if (typeof d === 'string') return d;
      if (d && typeof d === 'object') {
        const field = d.loc && d.loc.length > 1 ? `[${d.loc[d.loc.length - 1]}] ` : '';
        return `${field}${d.msg || JSON.stringify(d)}`;
      }
      return String(d);
    }).filter(Boolean);

    if (messages.length > 0) {
      return messages.join('. ');
    }
  }

  if (detail && typeof detail === 'object') {
    return detail.msg || detail.message || JSON.stringify(detail);
  }

  if (err.response?.data?.message && typeof err.response.data.message === 'string') {
    return err.response.data.message;
  }

  if (err.message && typeof err.message === 'string') {
    return err.message;
  }

  return defaultMsg;
}
