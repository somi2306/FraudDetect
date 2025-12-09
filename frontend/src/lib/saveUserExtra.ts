// src/lib/saveUserExtra.ts
import { supabase } from './supabaseClient';

export const saveUserExtra = async (
  clerkId: string,
  firstName: string,
  lastName: string,
  email: string,
  cin: string,
  rib: string,
  role: string,
  phone?: string
) => {
  const { data, error } = await supabase
    .from('users')
    .insert([
      {
        clerk_id: clerkId,
        first_name: firstName,
        last_name: lastName,
        email,
        phone,
        cin,
        rib,
        role
      }
    ]);

  if (error) throw error;
  return data;
};
