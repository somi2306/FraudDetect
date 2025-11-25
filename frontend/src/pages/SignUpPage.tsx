import { useSignUp } from "@clerk/clerk-react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

const schema = z.object({
  nom: z.string().min(1, { message: "Le nom est requis" }),
  prenom: z.string().min(1, { message: "Le prénom est requis" }),
  email: z.string().email({ message: "L'email n'est pas valide" }),
  password: z.string().min(8, { message: "Le mot de passe doit contenir au moins 8 caractères" }),
  cin: z.string().min(8, { message: "Le CIN doit contenir au moins 8 caractères" }),
  rib: z.string().min(20, { message: "Le RIB doit contenir au moins 20 caractères" }),
  telephone: z.string().min(8, { message: "Le numéro de téléphone doit contenir au moins 8 caractères" }),
  role: z.enum(["admin", "beneficiaire", "agent"]),
});

const verificationSchema = z.object({
  code: z.string().min(6, { message: "Le code doit contenir 6 caractères" }),
});

type FormData = z.infer<typeof schema>;
type VerificationFormData = z.infer<typeof verificationSchema>;

export default function SignUpPage() {
  const { isLoaded, signUp, setActive } = useSignUp();
  const [pendingVerification, setPendingVerification] = useState(false);
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      role: "beneficiaire",
    },
  });

  const {
    register: registerVerification,
    handleSubmit: handleSubmitVerification,
    formState: { errors: verificationErrors },
  } = useForm<VerificationFormData>({
    resolver: zodResolver(verificationSchema),
  });

  const onSubmit = async (data: FormData) => {
    if (!isLoaded) {
      return;
    }

    try {
      await signUp.create({
        emailAddress: data.email,
        password: data.password,
        unsafeMetadata: {
          nom: data.nom,
          prenom: data.prenom,
          cin: data.cin,
          rib: data.rib,
          telephone: data.telephone,
          role: data.role,
        },
      });

      await signUp.prepareEmailAddressVerification({ strategy: "email_code" });
      setPendingVerification(true);
    } catch (err: any) {
      console.error(JSON.stringify(err, null, 2));
    }
  };

  const onVerify = async (data: VerificationFormData) => {
    if (!isLoaded) {
      return;
    }

    try {
      const completeSignUp = await signUp.attemptEmailAddressVerification({
        code: data.code,
      });
      if (completeSignUp.status === "complete") {
        await setActive({ session: completeSignUp.createdSessionId });
        navigate("/dashboard");
      } else {
        console.error(JSON.stringify(completeSignUp, null, 2));
      }
    } catch (err: any) {
      console.error(JSON.stringify(err, null, 2));
    }
  };

  return (
    <div className="flex justify-center items-center h-screen">
      {!pendingVerification && (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label>Nom</label>
            <input {...register("nom")} className="border rounded p-2 w-full" />
            {errors.nom && <p className="text-red-500">{errors.nom.message}</p>}
          </div>
          <div>
            <label>Prénom</label>
            <input {...register("prenom")} className="border rounded p-2 w-full" />
            {errors.prenom && <p className="text-red-500">{errors.prenom.message}</p>}
          </div>
          <div>
            <label>Email</label>
            <input {...register("email")} className="border rounded p-2 w-full" />
            {errors.email && <p className="text-red-500">{errors.email.message}</p>}
          </div>
          <div>
            <label>Mot de passe</label>
            <input type="password" {...register("password")} className="border rounded p-2 w-full" />
            {errors.password && <p className="text-red-500">{errors.password.message}</p>}
          </div>
          <div>
            <label>CIN</label>
            <input {...register("cin")} className="border rounded p-2 w-full" />
            {errors.cin && <p className="text-red-500">{errors.cin.message}</p>}
          </div>
          <div>
            <label>RIB</label>
            <input {...register("rib")} className="border rounded p-2 w-full" />
            {errors.rib && <p className="text-red-500">{errors.rib.message}</p>}
          </div>
          <div>
            <label>Téléphone</label>
            <input {...register("telephone")} className="border rounded p-2 w-full" />
            {errors.telephone && <p className="text-red-500">{errors.telephone.message}</p>}
          </div>
          <div>
            <label>Role</label>
            <select {...register("role")} className="border rounded p-2 w-full">
              <option value="beneficiaire">Bénéficiaire</option>
            </select>
          </div>
          <button type="submit" className="bg-blue-500 text-white p-2 rounded w-full">
            Sign Up
          </button>
        </form>
      )}
      {pendingVerification && (
        <form onSubmit={handleSubmitVerification(onVerify)} className="space-y-4">
          <div>
            <label>Code de vérification</label>
            <input {...registerVerification("code")} className="border rounded p-2 w-full" />
            {verificationErrors.code && <p className="text-red-500">{verificationErrors.code.message}</p>}
          </div>
          <button type="submit" className="bg-blue-500 text-white p-2 rounded w-full">
            Vérifier
          </button>
        </form>
      )}
    </div>
  );
}
