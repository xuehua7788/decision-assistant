import API_BASE_URL from '../config/api';

export const analyzeDecision = async (decisionData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/decision`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(decisionData),
    });
    
    if (!response.ok) {
      throw new Error('API request failed');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Decision analysis error:', error);
    throw error;
  }
};

export const checkHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return await response.json();
  } catch (error) {
    console.error('Health check failed:', error);
    return { status: 'error' };
  }
};
