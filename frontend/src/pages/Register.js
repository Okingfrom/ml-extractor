import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Eye, 
  EyeOff, 
  Mail, 
  Lock, 
  User, 
  Phone, 
  ShoppingBag,
  Check,
  AlertCircle
} from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

const Register = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    password: '',
    confirm_password: '',
    account_type: 'free',
    terms_accepted: false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  const validateStep1 = () => {
    const newErrors = {};

    if (!formData.first_name) {
      newErrors.first_name = 'El nombre es requerido';
    }

    if (!formData.last_name) {
      newErrors.last_name = 'El apellido es requerido';
    }

    if (!formData.email) {
      newErrors.email = 'El email es requerido';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email inválido';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep2 = () => {
    const newErrors = {};

    if (!formData.password) {
      newErrors.password = 'La contraseña es requerida';
    } else if (formData.password.length < 8) {
      newErrors.password = 'La contraseña debe tener al menos 8 caracteres';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password = 'La contraseña debe contener al menos una mayúscula, una minúscula y un número';
    }

    if (!formData.confirm_password) {
      newErrors.confirm_password = 'Confirma tu contraseña';
    } else if (formData.password !== formData.confirm_password) {
      newErrors.confirm_password = 'Las contraseñas no coinciden';
    }

    if (!formData.terms_accepted) {
      newErrors.terms_accepted = 'Debes aceptar los términos y condiciones';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNextStep = () => {
    if (step === 1 && validateStep1()) {
      setStep(2);
    }
  };

  const handlePrevStep = () => {
    setStep(1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateStep2()) return;

    setIsLoading(true);
    
    try {
      const result = await register(formData);
      
      if (result.success) {
        navigate('/login', { 
          state: { 
            message: 'Registro exitoso. Revisa tu email para verificar tu cuenta.',
            type: 'success'
          }
        });
      } else {
        setErrors({ submit: result.error });
      }
    } catch (error) {
      setErrors({ submit: 'Error de conexión. Intenta nuevamente.' });
    } finally {
      setIsLoading(false);
    }
  };

  const getPasswordStrength = () => {
    const password = formData.password;
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^a-zA-Z\d]/.test(password)) strength++;
    
    return strength;
  };

  const getPasswordStrengthText = () => {
    const strength = getPasswordStrength();
    if (strength <= 2) return { text: 'Débil', color: 'text-error-600' };
    if (strength <= 3) return { text: 'Media', color: 'text-warning-600' };
    if (strength <= 4) return { text: 'Fuerte', color: 'text-success-600' };
    return { text: 'Muy fuerte', color: 'text-success-700' };
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Progress Indicator */}
        <div className="mb-6">
          <div className="flex items-center justify-center space-x-4">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
              step >= 1 ? 'bg-primary-600 text-white' : 'bg-secondary-200 text-secondary-500'
            }`}>
              1
            </div>
            <div className={`h-1 w-16 ${step >= 2 ? 'bg-primary-600' : 'bg-secondary-200'}`} />
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
              step >= 2 ? 'bg-primary-600 text-white' : 'bg-secondary-200 text-secondary-500'
            }`}>
              2
            </div>
          </div>
          <div className="text-center mt-2">
            <p className="text-sm text-secondary-600">
              Paso {step} de 2: {step === 1 ? 'Información personal' : 'Seguridad y tipo de cuenta'}
            </p>
          </div>
        </div>

        {/* Card */}
        <div className="ml-card p-8 space-y-6">
          {/* Header */}
          <div className="text-center space-y-2">
            <div className="w-16 h-16 ml-gradient rounded-2xl flex items-center justify-center mx-auto">
              <ShoppingBag className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-secondary-900">
              Crear Cuenta
            </h1>
            <p className="text-secondary-600">
              {step === 1 
                ? 'Completa tu información personal' 
                : 'Configura tu contraseña y tipo de cuenta'
              }
            </p>
          </div>

          {/* Form */}
          <form onSubmit={step === 2 ? handleSubmit : (e) => e.preventDefault()} className="space-y-4">
            {step === 1 && (
              <>
                {/* Name Fields */}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label htmlFor="first_name" className="block text-sm font-medium text-secondary-700 mb-1">
                      Nombre
                    </label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-secondary-400" />
                      <input
                        id="first_name"
                        name="first_name"
                        type="text"
                        value={formData.first_name}
                        onChange={handleChange}
                        className={`w-full pl-10 pr-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 ${
                          errors.first_name ? 'border-error-500' : 'border-secondary-300'
                        }`}
                        placeholder="Juan"
                      />
                    </div>
                    {errors.first_name && (
                      <p className="mt-1 text-sm text-error-600">{errors.first_name}</p>
                    )}
                  </div>

                  <div>
                    <label htmlFor="last_name" className="block text-sm font-medium text-secondary-700 mb-1">
                      Apellido
                    </label>
                    <input
                      id="last_name"
                      name="last_name"
                      type="text"
                      value={formData.last_name}
                      onChange={handleChange}
                      className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 ${
                        errors.last_name ? 'border-error-500' : 'border-secondary-300'
                      }`}
                      placeholder="Pérez"
                    />
                    {errors.last_name && (
                      <p className="mt-1 text-sm text-error-600">{errors.last_name}</p>
                    )}
                  </div>
                </div>

                {/* Email Field */}
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-secondary-700 mb-1">
                    Correo Electrónico
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-secondary-400" />
                    <input
                      id="email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleChange}
                      className={`w-full pl-10 pr-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 ${
                        errors.email ? 'border-error-500' : 'border-secondary-300'
                      }`}
                      placeholder="juan@email.com"
                    />
                  </div>
                  {errors.email && (
                    <p className="mt-1 text-sm text-error-600">{errors.email}</p>
                  )}
                </div>

                {/* Phone Field */}
                <div>
                  <label htmlFor="phone" className="block text-sm font-medium text-secondary-700 mb-1">
                    Teléfono (Opcional)
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-secondary-400" />
                    <input
                      id="phone"
                      name="phone"
                      type="tel"
                      value={formData.phone}
                      onChange={handleChange}
                      className="w-full pl-10 pr-4 py-3 border border-secondary-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
                      placeholder="+1 234 567 8900"
                    />
                  </div>
                </div>

                {/* Next Button */}
                <button
                  type="button"
                  onClick={handleNextStep}
                  className="w-full ml-gradient text-white font-medium py-3 px-4 rounded-xl hover:shadow-lg transform hover:scale-[1.02] transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
                >
                  Continuar
                </button>
              </>
            )}

            {step === 2 && (
              <>
                {/* Password Field */}
                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-secondary-700 mb-1">
                    Contraseña
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-secondary-400" />
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      value={formData.password}
                      onChange={handleChange}
                      className={`w-full pl-10 pr-10 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 ${
                        errors.password ? 'border-error-500' : 'border-secondary-300'
                      }`}
                      placeholder="Tu contraseña segura"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-secondary-400 hover:text-secondary-600"
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                  
                  {/* Password Strength */}
                  {formData.password && (
                    <div className="mt-2 space-y-1">
                      <div className="flex space-x-1">
                        {[1, 2, 3, 4, 5].map((level) => (
                          <div
                            key={level}
                            className={`h-1 flex-1 rounded ${
                              getPasswordStrength() >= level 
                                ? getPasswordStrength() <= 2 
                                  ? 'bg-error-500' 
                                  : getPasswordStrength() <= 3 
                                  ? 'bg-warning-500' 
                                  : 'bg-success-500'
                                : 'bg-secondary-200'
                            }`}
                          />
                        ))}
                      </div>
                      <p className={`text-xs font-medium ${getPasswordStrengthText().color}`}>
                        Seguridad: {getPasswordStrengthText().text}
                      </p>
                    </div>
                  )}
                  
                  {errors.password && (
                    <p className="mt-1 text-sm text-error-600">{errors.password}</p>
                  )}
                </div>

                {/* Confirm Password Field */}
                <div>
                  <label htmlFor="confirm_password" className="block text-sm font-medium text-secondary-700 mb-1">
                    Confirmar Contraseña
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-secondary-400" />
                    <input
                      id="confirm_password"
                      name="confirm_password"
                      type={showConfirmPassword ? 'text' : 'password'}
                      value={formData.confirm_password}
                      onChange={handleChange}
                      className={`w-full pl-10 pr-10 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 ${
                        errors.confirm_password ? 'border-error-500' : 'border-secondary-300'
                      }`}
                      placeholder="Confirma tu contraseña"
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-secondary-400 hover:text-secondary-600"
                    >
                      {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                  {errors.confirm_password && (
                    <p className="mt-1 text-sm text-error-600">{errors.confirm_password}</p>
                  )}
                </div>

                {/* Account Type */}
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-3">
                    Tipo de Cuenta
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    <label className={`relative flex items-center p-4 border rounded-xl cursor-pointer transition-all duration-200 ${
                      formData.account_type === 'free' 
                        ? 'border-primary-500 bg-primary-50' 
                        : 'border-secondary-300 hover:border-secondary-400'
                    }`}>
                      <input
                        type="radio"
                        name="account_type"
                        value="free"
                        checked={formData.account_type === 'free'}
                        onChange={handleChange}
                        className="sr-only"
                      />
                      <div className="flex-1">
                        <div className="font-medium text-secondary-900">Gratuita</div>
                        <div className="text-sm text-secondary-600">Funciones básicas</div>
                      </div>
                      {formData.account_type === 'free' && (
                        <Check className="w-5 h-5 text-primary-600" />
                      )}
                    </label>

                    <label className={`relative flex items-center p-4 border rounded-xl cursor-pointer transition-all duration-200 ${
                      formData.account_type === 'premium' 
                        ? 'border-primary-500 bg-primary-50' 
                        : 'border-secondary-300 hover:border-secondary-400'
                    }`}>
                      <input
                        type="radio"
                        name="account_type"
                        value="premium"
                        checked={formData.account_type === 'premium'}
                        onChange={handleChange}
                        className="sr-only"
                      />
                      <div className="flex-1">
                        <div className="font-medium text-secondary-900">Premium</div>
                        <div className="text-sm text-secondary-600">IA + Funciones avanzadas</div>
                      </div>
                      {formData.account_type === 'premium' && (
                        <Check className="w-5 h-5 text-primary-600" />
                      )}
                    </label>
                  </div>
                </div>

                {/* Terms Checkbox */}
                <div>
                  <label className="flex items-start space-x-3">
                    <input
                      type="checkbox"
                      name="terms_accepted"
                      checked={formData.terms_accepted}
                      onChange={handleChange}
                      className="mt-1 w-4 h-4 text-primary-600 border-secondary-300 rounded focus:ring-primary-500"
                    />
                    <span className="text-sm text-secondary-600">
                      Acepto los{' '}
                      <a href="#" className="text-primary-600 hover:text-primary-700 underline">
                        Términos y Condiciones
                      </a>{' '}
                      y la{' '}
                      <a href="#" className="text-primary-600 hover:text-primary-700 underline">
                        Política de Privacidad
                      </a>
                    </span>
                  </label>
                  {errors.terms_accepted && (
                    <p className="mt-1 text-sm text-error-600">{errors.terms_accepted}</p>
                  )}
                </div>

                {/* Submit Error */}
                {errors.submit && (
                  <div className="p-3 bg-error-50 border border-error-200 rounded-lg flex items-start space-x-2">
                    <AlertCircle className="w-5 h-5 text-error-600 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-error-700">{errors.submit}</p>
                  </div>
                )}

                {/* Buttons */}
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={handlePrevStep}
                    className="py-3 px-4 border border-secondary-300 text-secondary-700 font-medium rounded-xl hover:bg-secondary-50 transition-colors focus:outline-none focus:ring-2 focus:ring-secondary-500 focus:ring-offset-2"
                  >
                    Atrás
                  </button>
                  
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="ml-gradient text-white font-medium py-3 px-4 rounded-xl hover:shadow-lg transform hover:scale-[1.02] transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                  >
                    {isLoading ? (
                      <div className="flex items-center justify-center space-x-2">
                        <LoadingSpinner size="small" color="white" />
                        <span>Creando...</span>
                      </div>
                    ) : (
                      'Crear Cuenta'
                    )}
                  </button>
                </div>
              </>
            )}
          </form>

          {/* Footer Link */}
          <div className="text-center">
            <Link
              to="/login"
              className="text-primary-600 hover:text-primary-700 font-medium transition-colors"
            >
              ¿Ya tienes cuenta? Inicia sesión
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
