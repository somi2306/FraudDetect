import React, { useState, useRef, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Upload, FileImage, X, Building2, Loader } from 'lucide-react';
import { useBeneficiary } from '../BeneficiaryContext';
import { apiClient } from '@/lib/axios';
import { useAuth } from '@clerk/clerk-react';
import toast from 'react-hot-toast';

interface Bank {
  id: number;
  name: string;
}

const UploadModal = () => {
  const [banque, setBanque] = useState('');
  const [fichier, setFichier] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [open, setOpen] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [banks, setBanks] = useState<Bank[]>([]);
  const [loadingBanks, setLoadingBanks] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { refreshChecks } = useBeneficiary();
  const { getToken } = useAuth();

  // Fetch banks from backend
  useEffect(() => {
    const fetchBanks = async () => {
      setLoadingBanks(true);
      try {
        const token = await getToken();
        const response = await apiClient.get('/cheques/banks', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setBanks(response.data || []);
      } catch (error) {
        console.error('Error fetching banks:', error);
        // Fallback to hardcoded banks if API fails
        setBanks([
          { id: 1, name: 'Banque Populaire' },
          { id: 2, name: 'CIH' },
          { id: 3, name: 'Attijariwafa Bank' },
        ]);
      } finally {
        setLoadingBanks(false);
      }
    };

    if (open) {
      fetchBanks();
    }
  }, [open, getToken]);

  const handleFileChange = (file: File | null) => {
    setFichier(file);
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result as string);
      reader.readAsDataURL(file);
    } else {
      setPreview(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith('image/')) {
      handleFileChange(file);
    }
  };

  const handleSubmit = async () => {
    if (!banque || !fichier) return;

    setIsSubmitting(true);
    try {
      const token = await getToken();
      
      const formData = new FormData();
      formData.append('banque_name', banque);
      formData.append('file', fichier);

      await apiClient.post('/cheques/upload', formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      });

      toast.success('Chèque téléchargé avec succès!');
      
      // Reset form and close
      setBanque('');
      setFichier(null);
      setPreview(null);
      setOpen(false);
      
      // Refresh the cheques list
      refreshChecks();
    } catch (error: any) {
      console.error('Upload error:', error);
      const message = error.response?.data?.detail || 'Erreur lors du téléchargement';
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const clearFile = () => {
    setFichier(null);
    setPreview(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const isValid = banque && fichier && !isSubmitting;

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="bg-blue-600 text-white hover:bg-blue-700 shadow-md">
          <Upload className="mr-2 h-4 w-4" />
          Nouveau chèque
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader className="space-y-3 pb-4 border-b">
          <DialogTitle className="text-xl font-semibold text-center">
            Déposer un nouveau chèque
          </DialogTitle>
          <DialogDescription className="text-center text-gray-500">
            Sélectionnez la banque cible et téléchargez l'image du chèque
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-6">
          {/* Bank Selection */}
          <div className="space-y-2">
            <Label className="text-sm font-medium flex items-center gap-2">
              <Building2 className="h-4 w-4 text-gray-500" />
              Banque Ciblée
              <span className="text-red-500">*</span>
            </Label>
            <Select value={banque} onValueChange={setBanque} disabled={loadingBanks}>
              <SelectTrigger className="w-full h-11 border-gray-300 focus:ring-2 focus:ring-blue-500">
                <SelectValue placeholder={loadingBanks ? "Chargement..." : "Sélectionnez une banque"} />
              </SelectTrigger>
              <SelectContent>
                {banks.map((bank) => (
                  <SelectItem key={bank.id} value={bank.name}>
                    {bank.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* File Upload Area */}
          <div className="space-y-2">
            <Label className="text-sm font-medium flex items-center gap-2">
              <FileImage className="h-4 w-4 text-gray-500" />
              Image du chèque
              <span className="text-red-500">*</span>
            </Label>
            
            {!preview ? (
              <div
                className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer
                  ${isDragging 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
                  }`}
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
                  className="hidden"
                />
                <div className="flex flex-col items-center gap-3">
                  <div className="p-3 bg-blue-100 rounded-full">
                    <Upload className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700">
                      Glissez-déposez votre image ici
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      ou cliquez pour parcourir
                    </p>
                  </div>
                  <p className="text-xs text-gray-400">
                    PNG, JPG jusqu'à 10MB
                  </p>
                </div>
              </div>
            ) : (
              <div className="relative border rounded-xl overflow-hidden bg-gray-50">
                <img 
                  src={preview} 
                  alt="Aperçu du chèque" 
                  className="w-full h-48 object-contain"
                />
                <button
                  onClick={clearFile}
                  className="absolute top-2 right-2 p-1.5 bg-red-500 text-white rounded-full hover:bg-red-600 shadow-md transition"
                >
                  <X className="h-4 w-4" />
                </button>
                <div className="p-3 bg-white border-t">
                  <p className="text-sm text-gray-600 truncate">{fichier?.name}</p>
                  <p className="text-xs text-gray-400">
                    {fichier && (fichier.size / 1024).toFixed(1)} KB
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        <DialogFooter className="pt-4 border-t">
          <Button
            variant="outline"
            onClick={() => setOpen(false)}
            className="flex-1"
            disabled={isSubmitting}
          >
            Annuler
          </Button>
          <Button 
            onClick={handleSubmit} 
            disabled={!isValid}
            className={`flex-1 ${isValid 
              ? 'bg-blue-600 hover:bg-blue-700 text-white' 
              : 'bg-gray-200 text-gray-500 cursor-not-allowed'
            }`}
          >
            {isSubmitting ? (
              <>
                <Loader className="mr-2 h-4 w-4 animate-spin" />
                Envoi en cours...
              </>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" />
                Soumettre
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default UploadModal;
