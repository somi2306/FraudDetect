import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useBeneficiary } from '../BeneficiaryContext';

const Notifications = () => {
  const { notifications } = useBeneficiary();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Notifications</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {notifications.map((notif) => (
            <div
              key={notif.id}
              className={`p-4 border-l-4 ${
                !notif.lu ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
              }`}
            >
              <p className="font-semibold">{notif.message}</p>
              <p className="text-sm text-gray-500">{notif.date}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default Notifications;
