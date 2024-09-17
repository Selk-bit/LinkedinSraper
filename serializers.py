from pydantic import BaseModel, StringConstraints, ValidationError, PrivateAttr
from typing_extensions import Annotated
from typing import ClassVar, Optional  # Import ClassVar

from db_management.insert_data import session
from db_management.models import LinkedInCompany, LinkedInJob


class CompanySerializer(BaseModel):
    # Define fields using Annotated and StringConstraints for validation
    raison_social: Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]

    # Private attributes to store validation status and errors
    _validation_errors: str = PrivateAttr(default=None)
    _is_valid: bool = PrivateAttr(default=None)
    _validation_performed: bool = PrivateAttr(default=False)

    # Annotate 'model' as a ClassVar to indicate it's not a field
    model: ClassVar[type] = LinkedInCompany

    class Config:
        from_attributes = True

    def __init__(self, **data):
        super().__init__(**data)
        # Indicate that validation has already been performed during __init__
        self._validation_performed = True

    def validate(self) -> bool:
        """Custom validate method to manually trigger validation."""
        if getattr(self, '_validation_performed', False):
            raise Exception("Validation has already been performed during instantiation. Do not call validate() again.")
        try:
            # Validate the data
            validated_instance = self.__class__.model_validate(self.__dict__)
            # Update the instance with validated data
            self.__dict__.update(validated_instance.__dict__)
            self._is_valid = True
            # Set validation performed to True to prevent re-validation
            self._validation_performed = True
            return True
        except ValidationError as e:
            # Store validation errors and set validation status
            self._validation_errors = str(e)
            self._is_valid = False
            return False

    def errors_text(self) -> str:
        """Return the stored validation error messages."""
        return self._validation_errors

    def save(self):
        """Save the data after ensuring validation has been performed and passed."""
        # Check if validate has been called
        if self._is_valid is None:
            raise Exception("Validation has not been performed. Please call validate() before save().")
        # Check if validation passed
        if not self._is_valid:
            raise Exception(f"Cannot save invalid data. Validation errors: {self.errors_text()}")

        data = self.model_dump()

        # Create an instance of the LinkedInCompany model
        company = self.model(raison_social=data['raison_social'])
        session.add(company)
        session.commit()
        return company


###########################
class JobSerializer(BaseModel):
    # Define fields using Annotated and StringConstraints for validation
    title: Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]
    description: Optional[Annotated[str, StringConstraints(strip_whitespace=True)]] = None
    location: Optional[Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]] = None
    age: Optional[Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]] = None
    url: Annotated[str, StringConstraints(strip_whitespace=True)]  # Or use HttpUrl if you want URL validation
    company_id: Optional[int] = None
    transmitted: bool = False

    # Private attributes to store validation status and errors
    _validation_errors: str = PrivateAttr(default=None)
    _is_valid: bool = PrivateAttr(default=None)
    _validation_performed: bool = PrivateAttr(default=False)

    # Annotate 'model' as a ClassVar to indicate it's not a field
    model: ClassVar[type] = LinkedInJob

    class Config:
        from_attributes = True

    def __init__(self, **data):
        super().__init__(**data)
        # Indicate that validation has already been performed during __init__
        self._validation_performed = True

    def validate(self) -> bool:
        """Custom validate method to manually trigger validation."""
        if getattr(self, '_validation_performed', False):
            raise Exception("Validation has already been performed during instantiation. Do not call validate() again.")
        try:
            # Validate the data
            validated_instance = self.__class__.model_validate(self.__dict__)
            # Update the instance with validated data
            self.__dict__.update(validated_instance.__dict__)
            self._is_valid = True
            # Set validation performed to True to prevent re-validation
            self._validation_performed = True
            return True
        except ValidationError as e:
            # Store validation errors and set validation status
            self._validation_errors = str(e)
            self._is_valid = False
            return False

    def errors_text(self) -> str:
        """Return the stored validation error messages."""
        return self._validation_errors

    def save(self):
        """Save the data after ensuring validation has been performed and passed."""
        # Check if validate has been called
        if self._is_valid is None:
            raise Exception("Validation has not been performed. Please call validate() before save().")
        # Check if validation passed
        if not self._is_valid:
            raise Exception(f"Cannot save invalid data. Validation errors: {self.errors_text()}")

        data = self.model_dump()

        # Create an instance of the LinkedInJob model
        job = self.model(
            title=data['title'],
            description=data.get('description'),
            location=data.get('location'),
            age=data.get('age'),
            url=data['url'],
            company_id=data.get('company_id'),
            transmitted=data.get('transmitted', False)
        )

        session.add(job)
        session.commit()
        return job
