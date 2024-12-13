import { useState, useCallback } from 'react';

interface ValidationRules {
  [key: string]: (value: any) => string | null;
}

export function useForm<T extends Record<string, any>>(
  initialValues: T, 
  validationRules: ValidationRules = {}
) {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setValues(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));

    // Clear error when user starts typing
    if (errors[name as keyof T]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined
      }));
    }
  }, [errors]);

  const validate = useCallback(() => {
    const newErrors: Partial<Record<keyof T, string>> = {};

    Object.keys(validationRules).forEach(key => {
      const rule = validationRules[key];
      const error = rule(values[key]);
      if (error) {
        newErrors[key as keyof T] = error;
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [validationRules, values]);

  const handleSubmit = useCallback((
    submitHandler: (values: T) => Promise<void>,
    options: { 
      onSuccess?: () => void, 
      onError?: (error: any) => void 
    } = {}
  ) => async (e?: React.FormEvent) => {
    if (e) e.preventDefault();

    setIsSubmitting(true);
    
    try {
      if (validate()) {
        await submitHandler(values);
        options.onSuccess?.();
      }
    } catch (error) {
      options.onError?.(error);
    } finally {
      setIsSubmitting(false);
    }
  }, [validate, values]);

  const resetForm = useCallback(() => {
    setValues(initialValues);
    setErrors({});
  }, [initialValues]);

  return {
    values,
    errors,
    isSubmitting,
    handleChange,
    handleSubmit,
    resetForm,
    validate
  };
}

// Example validation rules
export const validationRules = {
  email: (value: string) => 
    !value ? 'Email is required' :
    !/\S+@\S+\.\S+/.test(value) ? 'Email is invalid' : null,
  
  password: (value: string) => 
    !value ? 'Password is required' :
    value.length < 8 ? 'Password must be at least 8 characters' : null
};