// src/utils/errorHandler.ts
export class AppError extends Error {
    constructor(
      message: string, 
      public status?: number
    ) {
      super(message);
      this.name = 'AppError';
    }
  }
  
  export const handleApiError = (error: any): AppError => {
    if (error.response) {
      return new AppError(
        error.response.data?.detail || 'An unexpected error occurred', 
        error.response.status
      );
    }
    return new AppError('Network error', 0);
  };