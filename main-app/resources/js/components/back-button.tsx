import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';

interface BackButtonProps {
    label?: string;
}

export default function BackButton({ label = 'Back' }: BackButtonProps) {
    const handleBack = () => {
        window.history.back();
    };

    return (
        <Button
            variant="ghost"
            size="sm"
            onClick={handleBack}
            className="gap-2"
        >
            <ArrowLeft className="h-4 w-4" />
            {label}
        </Button>
    );
}
