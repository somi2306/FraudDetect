CREATE TABLE checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc', now()) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    bank_name VARCHAR(255) NOT NULL,
    check_number VARCHAR(255) NOT NULL,
    beneficiary_id UUID NOT NULL, -- This will link the check to a user
    status VARCHAR(50) DEFAULT 'pending' NOT NULL, -- e.g., 'pending', 'approved', 'rejected'
    check_image_url VARCHAR(2048) -- URL of the uploaded check image
);

-- Optional: Add a comment to explain the table's purpose
COMMENT ON TABLE checks IS 'Stores information about uploaded checks from beneficiaries.';
