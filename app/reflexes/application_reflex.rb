class ApplicationReflex < StimulusReflex::Reflex
  include StimulusReflex::Reflex::CableReady
  include StimulusReflex::Reflex::ActionCable

  before_reflex do
    # Add any before_action-style logic here
  end

  after_reflex do
    # Add any after_action-style logic here
  end

  def self.before_reflex
    # Add any before_action-style logic here
  end

  def self.after_reflex
    # Add any after_action-style logic here
  end
end
