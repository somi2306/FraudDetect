import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Upload } from 'lucide-react';
import { useBeneficiary } from '../BeneficiaryContext';

const UploadModal = () => {
  const [numero, setNumero] = useState('');
  const [montant, setMontant] = useState('');
  const [banque, setBanque] = useState('');
  const [fichier, setFichier] = useState<File | null>(null);
  const { addCheck } = useBeneficiary();

  const handleSubmit = () => {
    addCheck({
      numero,
      montant: parseFloat(montant),
      banque,
      dateDepot: new Date().toISOString().split('T')[0],
      statut: 'en_attente',
    });
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="secondary">
          <Upload className="mr-2 h-4 w-4" />
          Nouveau chèque
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Télécharger un nouveau chèque</DialogTitle>
          <DialogDescription>
            Remplissez les informations ci-dessous pour soumettre un nouveau chèque.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="numero" className="text-right">
              Numéro
            </Label>
            <Input
              id="numero"
              value={numero}
              onChange={(e) => setNumero(e.target.value)}
              className="col-span-3"
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="montant" className="text-right">
              Montant
            </Label>
            <Input
              id="montant"
              type="number"
              value={montant}
              onChange={(e) => setMontant(e.target.value)}
              className="col-span-3"
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="banque" className="text-right">
              Banque
            </Label>
            <Input
              id="banque"
              value={banque}
              onChange={(e) => setBanque(e.target.value)}
              className="col-span-3"
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="fichier" className="text-right">
              Fichier
            </Label>
            <Input
              id="fichier"
              type="file"
              onChange={(e) => setFichier(e.target.files?.[0] || null)}
              className="col-span-3"
            />
          </div>
        </div>
        <Button type="submit" onClick={handleSubmit}>
          Soumettre
        </Button>
      </DialogContent>
    </Dialog>
  );
};

export default UploadModal;
