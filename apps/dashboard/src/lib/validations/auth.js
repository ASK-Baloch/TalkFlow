import { z } from "zod";

export const loginSchema = z.object({
  email: z
    .string()
    .trim()
    .min(1, { message: "Email address is required." })
    .email({ message: "Please enter a valid email address (e.g. name@company.com)." }),
  password: z
    .string()
    .min(1, { message: "Password is required." })
    .min(6, { message: "Password must be at least 6 characters long." }),
});

export function validateLoginForm(data) {
  const result = loginSchema.safeParse(data);
  if (!result.success) {
    const formattedErrors = {};
    result.error.issues.forEach((issue) => {
      const field = issue.path[0];
      if (!formattedErrors[field]) {
        formattedErrors[field] = issue.message;
      }
    });
    return { success: false, errors: formattedErrors };
  }
  return { success: true, data: result.data };
}

export const signupSchema = z.object({
  username: z
    .string()
    .trim()
    .min(1, { message: "Username is required." })
    .min(3, { message: "Username must be at least 3 characters." }),
  email: z
    .string()
    .trim()
    .min(1, { message: "Email address is required." })
    .email({ message: "Please enter a valid email address (e.g. name@company.com)." }),
  firstName: z
    .string()
    .trim()
    .min(1, { message: "First name is required." }),
  lastName: z
    .string()
    .trim()
    .min(1, { message: "Last name is required." }),
  password: z
    .string()
    .min(1, { message: "Password is required." })
    .min(6, { message: "Password must be at least 6 characters long." }),
});

export function validateSignupForm(data) {
  const result = signupSchema.safeParse(data);
  if (!result.success) {
    const formattedErrors = {};
    result.error.issues.forEach((issue) => {
      const field = issue.path[0];
      if (!formattedErrors[field]) {
        formattedErrors[field] = issue.message;
      }
    });
    return { success: false, errors: formattedErrors };
  }
  return { success: true, data: result.data };
}

export const registerSchema = z.object({
  username: z
    .string()
    .trim()
    .min(1, { message: "Username is required." })
    .min(3, { message: "Username must be at least 3 characters." }),
  email: z
    .string()
    .trim()
    .min(1, { message: "Email address is required." })
    .email({ message: "Please enter a valid email address (e.g. name@company.com)." }),
  firstName: z
    .string()
    .trim()
    .min(1, { message: "First name is required." }),
  lastName: z
    .string()
    .trim()
    .min(1, { message: "Last name is required." }),
  type: z.string().optional().default("REPORTING_USER"),
  password: z
    .string()
    .min(1, { message: "Password is required." })
    .min(6, { message: "Password must be at least 6 characters long." }),
});

export function validateRegisterForm(data) {
  const result = registerSchema.safeParse(data);
  if (!result.success) {
    const formattedErrors = {};
    result.error.issues.forEach((issue) => {
      const field = issue.path[0];
      if (!formattedErrors[field]) {
        formattedErrors[field] = issue.message;
      }
    });
    return { success: false, errors: formattedErrors };
  }
  return { success: true, data: result.data };
}

export function calculatePasswordStrength(password) {
  if (!password || password.length === 0) {
    return { score: 0, label: "", color: "bg-neutral-800", textColor: "text-neutral-500", percentage: 0 };
  }
  if (password.length < 6) {
    return { score: 1, label: "Weak (min 6 chars)", color: "bg-rose-500", textColor: "text-rose-400", percentage: 25 };
  }

  let score = 1;
  if (/[A-Z]/.test(password) && /[a-z]/.test(password)) score += 1;
  if (/[0-9]/.test(password)) score += 1;
  if (/[^A-Za-z0-9]/.test(password)) score += 1;
  if (password.length >= 10) score += 1;

  if (score <= 2) {
    return { score: 2, label: "Weak", color: "bg-rose-500", textColor: "text-rose-400", percentage: 33 };
  } else if (score === 3 || score === 4) {
    return { score: 3, label: "Moderate", color: "bg-amber-500", textColor: "text-amber-400", percentage: 66 };
  } else {
    return { score: 4, label: "Strong", color: "bg-emerald-500", textColor: "text-emerald-400", percentage: 100 };
  }
}

export const forgotPasswordSchema = z.object({
  email: z
    .string()
    .trim()
    .min(1, { message: "Email address is required." })
    .email({ message: "Please enter a valid email address (e.g. name@company.com)." }),
});

export function validateForgotPasswordForm(data) {
  const result = forgotPasswordSchema.safeParse(data);
  if (!result.success) {
    const formattedErrors = {};
    result.error.issues.forEach((issue) => {
      const field = issue.path[0];
      if (!formattedErrors[field]) {
        formattedErrors[field] = issue.message;
      }
    });
    return { success: false, errors: formattedErrors };
  }
  return { success: true, data: result.data };
}
